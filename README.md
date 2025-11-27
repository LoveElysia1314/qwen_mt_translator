# Qwen MT Translator

A Python library for text translation using Alibaba Cloud's Qwen MT API. This library provides efficient translation of both short paragraphs and long texts with intelligent chunking.

## Related Links

- [Qwen MT API Documentation](https://help.aliyun.com/zh/model-studio/qwen-mt-api)
- [Machine Translation Documentation](https://help.aliyun.com/zh/model-studio/machine-translation)
- [中文版](README_CN.md)

## Features

- **Intelligent Chunking**: Automatically splits long texts into optimal chunks for API processing
- *(Translation memory removed in this version)*
- **Configurable API Requests**: Customize translation parameters, terminology, and domains
- **CLI Interface**: Command-line tool for quick translations
- **Pure English**: All outputs and comments in English

## Installation

```bash
pip install -e .
```

Or install from source:

```bash
git clone https://github.com/LoveElysia1314/qwen-mt-translator.git
cd qwen-mt-translator
pip install -e .
```

## Quick Start

### CLI Usage

```bash
# Translate text from command line
qwen-translate "Hello world" --target-lang en

# Translate from file
qwen-translate -f input.txt -o output.txt

# Translate from stdin
echo "Some text" | qwen-translate

# Translate using a full API request JSON file
qwen-translate --request-json request.json
```

### Python API

#### Simple API (Recommended)

```python
from qwen_mt_translator import translate

# Simple translation with default settings
result = translate("你好世界", api_key="your-dashscope-api-key")
print(result)  # "Hello world"

# With custom config
result = translate(
    "你好世界",
    source_lang="Chinese",
    target_lang="English",
    api_key="your-dashscope-api-key"
)
print(result)

# Using config file
result = translate("你好世界", config="config.json")

# Get usage info
result = translate("你好世界", config="config.json", return_usage=True)
print(result["text"])  # Translated text
print(result["usage"])  # Token usage
```

#### Advanced API

```python
from qwen_mt_translator import TranslatorConfig, QwenMTTranslator

# Configure translator
config = TranslatorConfig(
    api_key="your-dashscope-api-key",
    source_lang="Chinese",
    target_lang="English"
)

# Create translator
translator = QwenMTTranslator(config)

# Translate text
result = translator.translate_text("你好世界")
print(result["text"])  # "Hello world"
print(result["usage"])  # Token usage info
```

## Configuration

Create a JSON configuration file with the new nested format:

```json
{
  "api": {
    "model": "qwen-mt-plus"
  },
  "translation": {
    "source_lang": "Chinese",
    "target_lang": "English",
    "domains": "general"
  },
  "terminology": {
    "terms": [
      {"source": "术语", "target": "Term"},
      {"source": "项目", "target": "Project"}
    ]
  },
  "tm_list": [
    {"source": "你好，欢迎使用。", "target": "Hello, welcome to use."}
  ]
}
```

Use with CLI:
```bash
qwen-translate -c config.json -f input.txt
```

## API Request JSON

For advanced usage, you can provide a full API request in JSON format:

```json
{
  "model": "qwen-mt-plus",
  "messages": [
    {
      "role": "user",
      "content": "Text to translate"
    }
  ],
  "extra_body": {
    "translation_options": {
      "source_lang": "zh",
      "target_lang": "en",
      "terms": [
        {
          "source": "术语",
          "target": "Term"
        }
      ]
    }
  },
  "stream": false
}
```

Use with CLI:
```bash
qwen-translate --request-json request.json
```

## API Reference

### translate()

Unified translation function for easy use.

- `text`: Text to translate
- `config`: Configuration (file path, dict, or TranslatorConfig object)
- `return_usage`: Return dict with usage info if True
- `**kwargs`: Config overrides

### TranslatorConfig

Configuration class for translator settings.

- `api_key`: DashScope API key (or set `ALIYUN_API_KEY` environment variable)
- `model`: Qwen MT model name (default: "qwen-mt-plus")
- `source_lang`: Source language (default: "zh")
- `target_lang`: Target language (default: "en")
- `domains`: Translation domain description (default: "general")
- `terms`: Dictionary of terminology mappings
- `tm_list`: List of translation memory examples
- `chunk_target_tokens`: Target tokens per chunk (hard-coded to 4000)

### QwenMTTranslator

Main translation class.

- `translate_segment(text)`: Translate a single text segment
- `translate_text(text)`: Translate text with automatic chunking

### TextChunker

Text chunking utility.

- `get_chunks(text)`: Split text into chunks
- `get_chunk_info(text)`: Get detailed chunk information

### TranslationMerger

Translation merging utility.

- `merge(chunk_translations)`: Merge chunk translations
- `merge_with_info(chunk_translations)`: Merge with detailed info

## Requirements

- Python 3.8+
- DashScope API key (from Alibaba Cloud)
- Dependencies: `openai`, `tiktoken`

## License

MIT License