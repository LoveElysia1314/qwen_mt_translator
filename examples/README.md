# Qwen MT Translator Demos

This directory contains demonstration scripts for the Qwen MT Translator library.

## Configuration Files

All configuration files are located in the `configs/` directory:

- `ranobe_config.json`: Configuration for light novel translation (Chinese to English)
- `readme_zh_to_en_config.json`: Configuration for README translation (Chinese to English)
- `readme_en_to_zh_config.json`: Configuration for README translation (English to Chinese)

## Demo Scripts

### 1. Light Novel Translation Demo (`ranobe_translation_demo.py`)

Demonstrates translation of Japanese light novel text with character name terminology.

**Features:**
- Loads configuration from JSON file
- Translates Chinese light novel excerpt from `ranobe_cn.md`
- Applies character name substitutions
 - Applies character name substitutions

**Usage:**
```bash
python examples/ranobe_translation_demo.py
```

### 2. README Translation Demo (`readme_translation_demo.py`)

Demonstrates bidirectional translation of project README files.

**Features:**
- Chinese to English README translation
- English to Chinese README translation
- Technical terminology handling
- Maintains code blocks and formatting

**Usage:**
```bash
python examples/readme_translation_demo.py
```

### 3. API Request JSON Demo (`request_example.json`)

Example JSON file for CLI --request-json option.

**Features:**
- Full API request specification
- Supports all OpenAI-compatible parameters
 - Can include translation_options and terms

**Usage:**
```bash
qwen-translate --request-json examples/request_example.json
```

## Configuration Support

The Qwen MT Translator supports loading configuration from JSON files using `TranslatorConfig.from_json()`. The configuration format includes:

- API settings (model, API key)
- Translation options (source/target languages, domains)
- Terminology dictionaries
 - Chunking settings

## Requirements

- Python 3.8+
- `ALIYUN_API_KEY` environment variable set with your DashScope API key
- `openai` and `tiktoken` packages

## Notes

- The translator automatically handles text chunking for long documents
 - API responses may include terminology information in the output