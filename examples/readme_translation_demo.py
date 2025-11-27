#!/usr/bin/env python3
"""
Demo: README Translation
Translates README files between Chinese and English using Qwen MT Translator.
"""

import os
import sys
from pathlib import Path

# Add the submodule to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qwen_mt_translator import TranslatorConfig, QwenMTTranslator


def translate_readme_zh_to_en():
    """Translate Chinese README to English"""
    print("=== Chinese to English README Translation ===")

    # Load configuration
    config_path = (
        Path(__file__).parent.parent / "config" / "readme_zh_to_en_config.json"
    )
    config = TranslatorConfig.from_json(str(config_path))

    if not config.api_key:
        config.api_key = os.getenv("ALIYUN_API_KEY")
        if not config.api_key:
            print("Error: ALIYUN_API_KEY environment variable not set")
            return

    translator = QwenMTTranslator(config)

    # Example Chinese README content
    zh_text = """# 项目名称

这是一个示例项目，用于演示翻译功能。

## 功能特性

- 功能1：描述功能1
- 功能2：描述功能2
- 功能3：描述功能3

## 安装方法

```bash
pip install 项目名称
```

## 使用方法

```python
import 项目名称

# 使用示例
```

## 配置说明

项目支持以下配置选项：

- option1: 配置选项1
- option2: 配置选项2

## 开发说明

### 依赖要求

- Python 3.8+
- 其他依赖包

### 运行测试

```bash
python -m pytest
```

## 贡献指南

欢迎提交问题和拉取请求！

## 许可证

MIT License"""

    print("Original Chinese README:")
    print(zh_text[:200] + "...\n")

    try:
        result = translator.translate_text(zh_text, use_memory=True)
        print("Translated English README:")
        print(result)
        return result
    except Exception as e:
        print(f"Translation failed: {e}")
        return None


def translate_readme_en_to_zh():
    """Translate English README to Chinese"""
    print("\n=== English to Chinese README Translation ===")

    # Load configuration
    config_path = (
        Path(__file__).parent.parent / "config" / "readme_en_to_zh_config.json"
    )
    config = TranslatorConfig.from_json(str(config_path))

    if not config.api_key:
        config.api_key = os.getenv("ALIYUN_API_KEY")
        if not config.api_key:
            print("Error: ALIYUN_API_KEY environment variable not set")
            return

    translator = QwenMTTranslator(config)

    # Example English README content
    en_text = """# Project Name

This is a sample project to demonstrate translation features.

## Features

- Feature 1: Description of feature 1
- Feature 2: Description of feature 2
- Feature 3: Description of feature 3

## Installation

```bash
pip install project-name
```

## Usage

```python
import project_name

# Usage example
```

## Configuration

The project supports the following configuration options:

- option1: Configuration option 1
- option2: Configuration option 2

## Development

### Requirements

- Python 3.8+
- Other dependencies

### Running Tests

```bash
python -m pytest
```

## Contributing

Issues and pull requests are welcome!

## License

MIT License"""

    print("Original English README:")
    print(en_text[:200] + "...\n")

    try:
        result = translator.translate_text(en_text, use_memory=True)
        print("Translated Chinese README:")
        print(result)
        return result
    except Exception as e:
        print(f"Translation failed: {e}")
        return None


def main():
    print("README Translation Demo")
    print("=" * 50)

    # Translate Chinese to English
    zh_to_en_result = translate_readme_zh_to_en()

    # Translate English to Chinese
    en_to_zh_result = translate_readme_en_to_zh()

    if zh_to_en_result and en_to_zh_result:
        print("\nBoth translations completed successfully!")
    else:
        print("\nSome translations failed.")


if __name__ == "__main__":
    main()
