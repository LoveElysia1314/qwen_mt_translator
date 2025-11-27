"""
Core translation functionality using Qwen MT API.
"""

import json
import logging
import re
import unicodedata
from typing import List, Dict, Optional, Any

from openai import OpenAI

from .chunker import TextChunker
from .merger import TranslationMerger
from .config import TranslatorConfig

logger = logging.getLogger(__name__)


def normalize_english_text(text: str) -> str:
    """
    Normalize English text by converting full-width characters to half-width,
    standardizing quotation marks, and cleaning up repeated punctuation.

    This function is useful for post-processing translated text to ensure
    consistent punctuation and character width.

    Args:
        text: The text to normalize.

    Returns:
        Normalized text.
    """
    # Use NFKC normalization to convert full-width to half-width
    text = unicodedata.normalize('NFKC', text)

    # Additional mappings for curly quotes and other punctuation
    text = text.replace('\u2018', "'")  # Left single quotation mark
    text = text.replace('\u2019', "'")  # Right single quotation mark
    text = text.replace('\u201c', '"')  # Left double quotation mark
    text = text.replace('\u201d', '"')  # Right double quotation mark
    text = text.replace('\u201b', "'")  # Single high-reversed-9 quotation mark
    text = text.replace('\u201f', "'")  # Single low-9 quotation mark
    text = text.replace('\u201e', '"')  # Double low-9 quotation mark

    # Clean up repeated punctuation marks (e.g., multiple quotes)
    text = re.sub(r'("+)', '"', text)  # Replace multiple double quotes with single
    text = re.sub(r"('+)", "'", text)  # Replace multiple single quotes with single

    return text


class QwenMTTranslator:
    """Qwen MT translator with chunking."""

    def __init__(self, config: TranslatorConfig):
        """
        Initialize translator.

        Args:
            config: TranslatorConfig instance
        """
        self.config = config

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=config.api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        # Initialize utilities
        self.chunker = TextChunker(target_tokens=config.chunk_target_tokens)
        self.merger = TranslationMerger()

        # Translation memory removed: no local TM maintained

    def translate_segment(self, text: str) -> Dict[str, Any]:
        """
        Translate a single segment.

        Args:
            text: Text to translate

        Returns:
            Dict with 'text' (translated text) and 'usage' (token usage)
        """
        # Build translation options
        current_translation_options = {
            "source_lang": self.config.source_lang,
            "target_lang": self.config.target_lang,
            "domains": self.config.domains,
        }

        if self.config.terms:
            # Convert terms dict to list format expected by API
            terms_list = [
                {"source": k, "target": v} for k, v in self.config.terms.items()
            ]
            current_translation_options["terms"] = terms_list

        # Include static translation memory list from config if present
        try:
            if getattr(self.config, "tm_list", None):
                current_translation_options["tm_list"] = self.config.tm_list
        except Exception:
            pass


        # Build messages
        messages = [{"role": "user", "content": text}]

        # Debug logging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("API Request translation_options:")
            logger.debug(json.dumps(current_translation_options, ensure_ascii=False))

        # Log translation_options for debug (use logger instead of print)
        if logger.isEnabledFor(logging.DEBUG):
            try:
                logger.debug(
                    "DEBUG translation_options: %s",
                    json.dumps(current_translation_options, ensure_ascii=False),
                )
            except Exception:
                logger.debug("DEBUG translation_options: <failed to serialize>")
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                extra_body={"translation_options": current_translation_options},
                stream=False,
            )

            api_response = response.choices[0].message.content

            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("API raw response length: %d", len(api_response))
                logger.debug("API raw response: %s", api_response)

            translated_text = self._extract_api_response(api_response)
            usage = response.usage

            return {
                "text": translated_text,
                "usage": {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
            }

        except Exception as e:
            raise RuntimeError(f"Translation failed: {str(e)}")

    def translate_text(self, text: str) -> Dict[str, Any]:
        """Translate text with chunking.

        Args:
            text: Input text

        Returns:
            Dict with 'text' (translated text) and 'usage' (total token usage)
        """
        # For short text, translate directly
        if len(text.split()) < 100:  # Rough estimate
            result = self.translate_segment(text)
            result["text"] = self._post_process_translation(result["text"])
            return result

        # For long text, use chunking
        chunks = self.chunker.get_chunks(text)

        if len(chunks) == 1:
            result = self.translate_segment(text)
            return result

        # Translate chunks
        translated_chunks = []
        total_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        for chunk_text, start_line, end_line in chunks:
            result = self.translate_segment(chunk_text)
            translated_chunks.append(result["text"])

            # Accumulate usage
            for key in total_usage:
                total_usage[key] += result["usage"][key]

        # Merge results
        merged_text = self.merger.merge(translated_chunks)
        merged_text = self._post_process_translation(merged_text)
        return {"text": merged_text, "usage": total_usage}

    def _post_process_translation(self, text: str) -> str:
        """
        Post-process translated text for English target language.
        Convert full-width characters to half-width using Unicode normalization,
        and clean up repeated punctuation marks.

        Args:
            text: Translated text

        Returns:
            Post-processed text
        """
        if self.config.target_lang.lower() != "en":
            return text

        return normalize_english_text(text)

    def _extract_api_response(self, text: str) -> str:
        """
        从API响应中提取翻译内容并清理可能的前言/术语表回显。

        如果模型在返回中包含 domain 描述、说明句或按行打印的 JSON 术语对（含 src/tgt），
        则删除这些前缀并返回净文本。
        """
        if not text:
            return text

        lines = text.splitlines()

        # Try to detect and skip a domain line if present (exact or containing)
        start = 0
        try:
            domain_cfg = getattr(self.config, "domains", None)
        except Exception:
            domain_cfg = None

        domain_str = None
        if domain_cfg:
            domain_str = (
                domain_cfg
                if isinstance(domain_cfg, str)
                else (domain_cfg[0] if len(domain_cfg) > 0 else None)
            )

        if (
            domain_str
            and domain_str.strip()
            and domain_str.strip() in (lines[0] if lines else "")
        ):
            start = 1

        # 使用正则表达式更精确地检测前言行
        import re
        glossary_intro_pattern = re.compile(
            r"I've included some words.*bilingual dictionary.*Please translate.*",
            re.IGNORECASE
        )

        while start < len(lines) and glossary_intro_pattern.search(lines[start]):
            start += 1

        # 更精确地检测术语表行：匹配 {"src": "...", "tgt": "..."} 格式
        glossary_line_pattern = re.compile(
            r'^\s*\{\s*"src"\s*:\s*".*?"\s*,\s*"tgt"\s*:\s*".*?"\s*\}\s*$'
        )

        # 跳过连续的术语表行和空白行
        while start < len(lines) and (
            glossary_line_pattern.match(lines[start]) or not lines[start].strip()
        ):
            start += 1

        cleaned = "\n".join(lines[start:]).lstrip("\n")

        # 如果过滤后没有有效内容，记录警告并返回空字符串或抛出异常
        if not cleaned.strip():
            logger.warning("API response contained only glossary/description, no translation content found")
            return ""  # 或 raise ValueError("Invalid API response: no translation content")

        return cleaned

