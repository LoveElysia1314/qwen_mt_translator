"""
Configuration handling for Qwen MT Translator.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, List


class TranslatorConfig:
    """Configuration class for translator settings."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "qwen-mt-plus",
        source_lang: str = "zh",
        target_lang: str = "en",
        domains: Optional[str] = None,
        terms: Optional[Dict[str, str]] = None,
        tm_list: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Initialize translator configuration.

        Args:
            api_key: DashScope API key
            model: Qwen MT model name
            source_lang: Source language
            target_lang: Target language
            domains: Translation domain description (string)
            terms: Terminology dictionary
            chunk_target_tokens: Target tokens per chunk
            
        """
        self.api_key = api_key or os.getenv("ALIYUN_API_KEY")
        if not self.api_key:
            raise ValueError("API key not provided and ALIYUN_API_KEY not set")

        self.model = model
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.domains = domains or "general"
        self.terms = terms or {}
        # Chunk target tokens hard-coded to 4000 per project policy
        self.chunk_target_tokens = 4000
        self.tm_list = tm_list or []
        

    @classmethod
    def from_json_dict(cls, data: Dict) -> "TranslatorConfig":
        """
        Load configuration from dictionary.

        Args:
            data: Config dictionary

        Returns:
            TranslatorConfig instance
        """
        # Extract nested config
        api_config = data.get("api", {})
        translation_config = data.get(
            "translation", data.get("translation_options", {})
        )
        terminology_config = data.get("terminology", {})

        domains_raw = translation_config.get("domains", "general")
        if isinstance(domains_raw, list):
            domains = domains_raw[0] if domains_raw else "general"
        else:
            domains = domains_raw

        # Handle terms: can be dict or list of dicts
        terms_raw = terminology_config.get("terms", {})
        if isinstance(terms_raw, list):
            terms = {item["source"]: item["target"] for item in terms_raw}
        else:
            terms = terms_raw

        return cls(
            api_key=data.get("api_key"),
            model=api_config.get("model", "qwen-mt-plus"),
            source_lang=translation_config.get("source_lang", "zh"),
            target_lang=translation_config.get("target_lang", "en"),
            domains=domains,
            terms=terms,
            tm_list=translation_config.get("tm_list", data.get("tm_list", [])),
        )

    def to_dict(self) -> Dict:
        """Convert config to dictionary."""
        # Convert terms dict to list format for export
        terms_list = [{"source": k, "target": v} for k, v in self.terms.items()]
        return {
            "api_key": self.api_key,
            "model": self.model,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "domains": self.domains,
            "terms": terms_list,
            "tm_list": self.tm_list,
            
        }
