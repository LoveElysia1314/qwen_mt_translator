"""
Translation merging utilities.
"""

from typing import List, Dict, Tuple


class TranslationMerger:
    """Translation merger for combining chunked translations."""

    def merge(self, chunk_translations: List[str]) -> str:
        """
        Merge chunk translations.

        Strategy: Direct concatenation of all chunks.

        Args:
            chunk_translations: List of chunk translation strings

        Returns:
            Merged translation text
        """
        return "\n".join(chunk_translations)

    def merge_with_info(self, chunk_translations: List[str]) -> Tuple[str, Dict]:
        """
        Merge translations with detailed info.

        Args:
            chunk_translations: List of chunk translation strings

        Returns:
            Tuple of (merged_translation, merge_info)
        """
        merged = self.merge(chunk_translations)

        info = {
            "chunk_count": len(chunk_translations),
            "total_length": len(merged),
            "chunks_info": [],
        }

        for i, translation in enumerate(chunk_translations, 1):
            info["chunks_info"].append(
                {
                    "index": i,
                    "original_lines": len(translation.split("\n")),
                    "original_length": len(translation),
                }
            )

        return merged, info
