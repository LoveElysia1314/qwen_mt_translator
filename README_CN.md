# 通义机器翻译器

一个基于阿里云通义千问机器翻译API的Python库。该库提供高效的文本翻译功能，支持短段落和长文本的翻译，并具备智能分块功能。

## 相关链接

- [通义千问机器翻译API文档](https://help.aliyun.com/zh/model-studio/qwen-mt-api)
- [机器翻译文档](https://help.aliyun.com/zh/model-studio/machine-translation)
- [English Version](README.md)

## 功能特性

- **智能分块**：自动将长文本分割成最适合API处理的块
- *(翻译记忆功能已在此版本移除)*
- **可配置API请求**：自定义翻译参数、术语和领域
- **命令行界面**：快速进行文本翻译的命令行工具
- **纯英文**：所有输出和注释均采用英文

## 安装

```bash
pip install -e .
```

或从源码安装：

```bash
git clone https://github.com/LoveElysia1314/qwen-mt-translator.git
cd qwen-mt-translator
pip install -e .
```

## 快速入门

### 命令行使用

```bash
# 从命令行直接翻译文本
qwen-translate "Hello world" --target-lang en

# 从文件中翻译
qwen-translate -f input.txt -o output.txt

# 从标准输入翻译
echo "Some text" | qwen-translate

# 使用完整的API请求JSON文件进行翻译
qwen-translate --request-json request.json
```

### Python API

```python
from qwen_mt_translator import TranslatorConfig, QwenMTTranslator

# 配置翻译器
config = TranslatorConfig(
    api_key="your-dashscope-api-key",
    source_lang="zh",
    target_lang="en"
)

# 创建翻译器
translator = QwenMTTranslator(config)

# 翻译文本
result = translator.translate_text("你好世界")
print(result)  # "Hello world"
```

## 配置

创建一个JSON配置文件：

```json
{
  "api_key": "your-dashscope-api-key",
  "model": "qwen-mt-plus",
  "source_lang": "zh",
  "target_lang": "en",
  "domains": ["general"],
  "terms": {
    "术语": "Term"
  },
  "chunk_target_tokens": 3500
}
```

与命令行结合使用：
```bash
qwen-translate -c config.json -f input.txt
```

## API请求JSON

对于高级用法，您可以提供一个完整的API请求JSON格式：

```json
{
  "model": "qwen-mt-plus",
  "messages": [
    {
      "role": "user",
      "content": "待翻译文本"
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

与命令行结合使用：
```bash
qwen-translate --request-json request.json
```

## API参考

### TranslatorConfig

翻译器设置的配置类。

- `api_key`: DashScope API密钥（或设置`ALIYUN_API_KEY`环境变量）
- `model`: 通义千问机器翻译模型名称（默认："qwen-mt-plus"）
- `source_lang`: 源语言代码（默认："zh"）
- `target_lang`: 目标语言代码（默认："en"）
- `domains`: 翻译领域列表（默认：["general"]）
- `terms`: 术语映射字典
`chunk_target_tokens`: 每个分块的目标token数（默认：3500）

### QwenMTTranslator

主要的翻译类。

`translate_segment(text)`: 翻译单个文本片段
`translate_text(text)`: 自动分块并翻译文本

### TextChunker

文本分块工具。

- `get_chunks(text)`: 将文本分割成多个块
- `get_chunk_info(text)`: 获取详细的分块信息

### TranslationMerger

翻译合并工具。

- `merge(chunk_translations)`: 合并分块翻译结果
- `merge_with_info(chunk_translations)`: 带详细信息的合并

## 系统要求

- Python 3.8+
- DashScope API密钥（来自阿里云）
- 依赖库：`openai`、`tiktoken`

## 许可证

MIT许可证