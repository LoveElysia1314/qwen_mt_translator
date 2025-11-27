#!/usr/bin/env python3
"""
Demo: Light Novel Translation
Translates a Chinese light novel chapter using Qwen MT Translator.
"""

import os
import sys
from pathlib import Path

# Add the submodule to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qwen_mt_translator import TranslatorConfig, QwenMTTranslator


def main():
    # Load configuration from file
    config_path = Path(__file__).parent / "configs" / "ranobe_config.json"
    config = TranslatorConfig.from_json(str(config_path))

    # Set API key from environment if not in config
    if not config.api_key:
        config.api_key = os.getenv("ALIYUN_API_KEY")
        if not config.api_key:
            print("Error: ALIYUN_API_KEY environment variable not set")
            return

    # Create translator
    translator = QwenMTTranslator(config)

    # Load light novel text from file
    text_path = Path(__file__).parent / "ranobe_cn.md"
    if not text_path.exists():
        print(f"Error: Text file '{text_path}' not found")
        return

    with open(text_path, "r", encoding="utf-8") as f:
        text = f.read()

    print("=== Light Novel Translation Demo ===")
    print("Loading text from ranobe_cn.md...")
    print(f"Text length: {len(text)} characters")
    print("\nTranslating...")

    try:
        # Translate
        result = translator.translate_text(text, use_memory=True)
        print("\nTranslated English text:")
        print(result)
        print("\nTranslation completed successfully!")

    except Exception as e:
        print(f"Translation failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
