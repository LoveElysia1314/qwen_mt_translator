#!/usr/bin/env python3
"""
Example usage of Qwen MT Translator library.
"""

from qwen_mt_translator import TranslatorConfig, QwenMTTranslator


def main():
    # Example configuration (replace with your actual API key)
    config = TranslatorConfig(
        api_key="your-dashscope-api-key-here",  # Replace with actual key
        source_lang="zh",
        target_lang="en",
        domains=["general"],
        terms={"人工智能": "AI", "机器学习": "Machine Learning"},
    )

    # Create translator
    translator = QwenMTTranslator(config)

    # Example text
    text = """这是一个测试文本。
    它包含多行内容。
    用于演示翻译功能。"""

    print("Original text:")
    print(text)
    print("\nTranslating...")

    try:
        # Translate
        result = translator.translate_text(text, use_memory=True)
        print("\nTranslated text:")
        print(result)
    except Exception as e:
        print(f"Translation failed: {e}")
        print("Note: Make sure to set a valid API key")


if __name__ == "__main__":
    main()
