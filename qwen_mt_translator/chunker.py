"""
Text chunking utilities for translation.
"""

import math
import tiktoken
from typing import List, Tuple, Dict


class TextChunker:
    """Text chunker.

    Supports two splitting strategies:
    - 贪心（按行累加，接近目标 token）
    - 动态规划（DP）最优分割：在行边界上最小化最大块 token
    """

    def __init__(
        self,
        target_tokens: int = 3500,
        encoding_name: str = "cl100k_base",
        use_dp: bool = True,
    ):
        """
        Initialize text chunker.

        Args:
            target_tokens: Target tokens per chunk (default 3500)
            encoding_name: Tiktoken encoding name (default cl100k_base)
        """
        self.target_tokens = target_tokens
        self.encoding = tiktoken.get_encoding(encoding_name)
        self.use_dp = use_dp

    def split_text(self, text: str) -> List[Tuple[int, int, int]]:
        """
        Split text into chunks.

        Args:
            text: Input text

        Returns:
            List of (start_line, end_line, token_count) tuples
        """
        lines = text.splitlines()

        if not lines:
            return []

        line_tokens = self._compute_line_tokens(lines)
        if self.use_dp:
            split_points = self._optimal_split(lines, line_tokens)
        else:
            split_points = self._greedy_split(lines, line_tokens)

        return split_points

    def _optimal_split(self, lines: List[str], line_tokens: List[int]) -> List[Tuple[int, int, int]]:
        """
        Use dynamic programming to partition lines into k contiguous chunks (line-level)
        so that the maximum chunk token count is minimized (linear partition problem).

        The number of chunks k is estimated from preferred limit (<=4000) but will be
        increased if necessary to ensure no chunk exceeds HARD_LIMIT (8000), because
        we cannot split inside a line.
        """
        n = len(line_tokens)
        if n == 0:
            return []

        total_tokens = sum(line_tokens)

        PREFERRED_LIMIT = min(self.target_tokens, 4000)
        HARD_LIMIT = 8000

        # initial estimate
        estimated_k = max(1, math.ceil(total_tokens / PREFERRED_LIMIT))
        min_k = max(1, math.ceil(total_tokens / HARD_LIMIT))
        k = max(estimated_k, min_k)

        # prefix sums for quick range sum
        ps = [0] * (n + 1)
        for i in range(1, n + 1):
            ps[i] = ps[i - 1] + line_tokens[i - 1]

        # helper to run DP for given k
        def run_dp(k_parts: int):
            # dp[i][j]: minimal possible largest sum when partitioning first i items into j parts
            dp = [[float("inf")] * (k_parts + 1) for _ in range(n + 1)]
            div = [[0] * (k_parts + 1) for _ in range(n + 1)]

            dp[0][0] = 0
            for i in range(1, n + 1):
                dp[i][1] = ps[i]
                div[i][1] = 0

            for j in range(2, k_parts + 1):
                # i must be at least j
                for i in range(j, n + 1):
                    best = float("inf")
                    best_x = j - 1
                    # try possible split points x (number of items in first j-1 parts)
                    # x ranges from j-1 to i-1
                    for x in range(j - 1, i):
                        cost = max(dp[x][j - 1], ps[i] - ps[x])
                        if cost < best:
                            best = cost
                            best_x = x
                    dp[i][j] = best
                    div[i][j] = best_x

            # reconstruct partitions
            parts = []
            idx = n
            for j in range(k_parts, 0, -1):
                x = div[idx][j]
                start = x
                end = idx - 1
                tokens = ps[idx] - ps[x]
                parts.append((start, end, tokens))
                idx = x

            parts.reverse()
            return dp[n][k_parts], parts

        # Try increasing k until we satisfy HARD_LIMIT or reach n (one line per chunk)
        while k <= n:
            max_chunk_tok, parts = run_dp(k)
            if max_chunk_tok <= HARD_LIMIT or k == n:
                return parts
            k += 1

        # fallback
        return [(i, i, line_tokens[i]) for i in range(n)]

    def _compute_line_tokens(self, lines: List[str]) -> List[int]:
        """Compute tokens for each line."""
        return [len(self.encoding.encode(line)) for line in lines]

    def _greedy_split(
        self,
        lines: List[str],
        line_tokens: List[int],
    ) -> List[Tuple[int, int, int]]:
        """
        Greedy splitting algorithm.

        Strategy:
        1. Start from beginning
        2. Accumulate lines until approaching target_tokens
        3. Repeat until end
        """
        split_points: List[Tuple[int, int, int]] = []

        total_lines = len(lines)
        if total_lines == 0:
            return split_points

        total_tokens = sum(line_tokens)

        # Limits: preferred per-chunk limit and hard limit (tokens)
        PREFERRED_LIMIT = min(self.target_tokens, 4000)
        HARD_LIMIT = 8000

        # Compute initial estimated number of chunks
        estimated_chunks = max(1, math.ceil(total_tokens / PREFERRED_LIMIT))

        # Compute target tokens per chunk (ideal)
        target_per_chunk = math.ceil(total_tokens / estimated_chunks)

        # Allow a small slack (10%) but never exceed HARD_LIMIT
        slack = max(50, int(0.1 * target_per_chunk))
        threshold = min(HARD_LIMIT, target_per_chunk + slack)

        current_start = 0
        i = 0

        while current_start < total_lines:
            accumulated_tokens = 0
            end_line = current_start

            for j in range(current_start, total_lines):
                tok = line_tokens[j]

                # If single line itself exceeds hard limit, allow it but place as a single chunk
                if tok > HARD_LIMIT:
                    end_line = j
                    accumulated_tokens = tok
                    break

                # If adding this line would exceed threshold, decide whether to include it
                if accumulated_tokens + tok > threshold:
                    if j == current_start:
                        # first line of the chunk exceeds threshold but <= HARD_LIMIT
                        end_line = j
                        accumulated_tokens += tok
                    else:
                        without_last = accumulated_tokens
                        with_last = accumulated_tokens + tok

                        # Choose the option closer to target_per_chunk, but never exceed HARD_LIMIT
                        if abs(without_last - target_per_chunk) <= abs(with_last - target_per_chunk):
                            end_line = j - 1
                            accumulated_tokens = without_last
                        else:
                            # only accept with_last if it doesn't exceed HARD_LIMIT
                            if with_last <= HARD_LIMIT:
                                end_line = j
                                accumulated_tokens = with_last
                            else:
                                end_line = j - 1
                                accumulated_tokens = without_last
                    break

                accumulated_tokens += tok
                end_line = j

            split_points.append((current_start, end_line, accumulated_tokens))

            # Prepare for next chunk
            current_start = end_line + 1

            # Recompute remaining tokens and adjust target if needed to avoid too many small chunks
            remaining_tokens = sum(line_tokens[current_start:]) if current_start < total_lines else 0
            remaining_chunks = max(1, estimated_chunks - len(split_points))
            if remaining_tokens > 0:
                # Recalculate target per remaining chunk conservatively
                target_per_chunk = math.ceil(remaining_tokens / remaining_chunks)
                slack = max(50, int(0.1 * target_per_chunk))
                threshold = min(HARD_LIMIT, target_per_chunk + slack)

            i += 1

        return split_points

    def get_chunks(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Get text chunks.

        Args:
            text: Input text

        Returns:
            List of (chunk_text, start_line, end_line) tuples
        """
        lines = text.splitlines()
        split_points = self.split_text(text)

        chunks = []
        for start_line, end_line, _ in split_points:
            chunk_lines = lines[start_line : end_line + 1]
            chunk_text = "\n".join(chunk_lines)
            chunks.append((chunk_text, start_line, end_line))

        return chunks

    def get_chunk_info(self, text: str) -> List[Dict]:
        """
        Get detailed chunk information.

        Args:
            text: Input text

        Returns:
            List of chunk info dictionaries
        """
        lines = text.splitlines()
        split_points = self.split_text(text)

        info_list = []
        for i, (start_line, end_line, tokens) in enumerate(split_points, 1):
            chunk_lines = lines[start_line : end_line + 1]
            chunk_text = "\n".join(chunk_lines)

            info_list.append(
                {
                    "index": i,
                    "start_line": start_line + 1,  # 1-based
                    "end_line": end_line + 1,  # 1-based
                    "line_count": end_line - start_line + 1,
                    "tokens": tokens,
                    "text": chunk_text,
                }
            )

        return info_list
