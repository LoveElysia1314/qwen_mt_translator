"""
Qwen MT Translator - A Python library for text translation using Qwen MT API.

This library provides core translation functionality with chunking, translation memory,
and configurable API requests.
"""

__version__ = "0.1.0"

from typing import Union, Dict, Any
import json
from pathlib import Path

from .config import TranslatorConfig
from .core import QwenMTTranslator, normalize_english_text
from .chunker import TextChunker
from .merger import TranslationMerger


def translate(
    text: str,
    config: Union[str, Dict[str, Any], TranslatorConfig, None] = None,
    return_usage: bool = False,
    **kwargs
) -> Union[str, Dict[str, Any]]:
    """
    Unified translation API for easy use.

    Args:
        text: Text to translate
        config: Configuration - can be:
            - str: path to JSON config file
            - dict: config dictionary
            - TranslatorConfig: config object
            - None: use default config with kwargs overrides
        return_usage: If True, return dict with 'text' and 'usage', else return text only
        **kwargs: Additional config overrides (api_key, model, source_lang, etc.)

    Returns:
        Translated text or dict with 'text' and 'usage'

    Example:
        >>> from qwen_mt_translator import translate
        >>> result = translate("你好世界", source_lang="Chinese", target_lang="English")
        >>> print(result)
        Hello world
    """
    # Handle config
    if isinstance(config, str):
        # Load from file
        config_path = Path(config)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config}")
        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        translator_config = TranslatorConfig.from_json_dict(config_dict)
    elif isinstance(config, dict):
        translator_config = TranslatorConfig.from_json_dict(config)
    elif isinstance(config, TranslatorConfig):
        translator_config = config
    else:
        translator_config = TranslatorConfig()

    # Apply kwargs overrides
    for key, value in kwargs.items():
        if hasattr(translator_config, key):
            setattr(translator_config, key, value)

    # Create translator and translate
    translator = QwenMTTranslator(translator_config)
    result = translator.translate_text(text)
    if return_usage:
        return result
    else:
        return result["text"]


__all__ = [
    "TranslatorConfig",
    "QwenMTTranslator",
    "normalize_english_text",
    "TextChunker",
    "TranslationMerger",
    "translate",
]
