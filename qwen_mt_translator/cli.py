"""
Command-line interface for Qwen MT Translator.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from openai import OpenAI

from .config import TranslatorConfig
from .core import QwenMTTranslator


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Qwen MT Translator - Translate text using Qwen MT API"
    )

    parser.add_argument(
        "text", nargs="?", help="Text to translate (if not provided, read from stdin)"
    )

    parser.add_argument("-f", "--file", type=str, help="Input file to translate")

    parser.add_argument(
        "-o", "--output", type=str, help="Output file (default: stdout)"
    )

    parser.add_argument("-c", "--config", type=str, help="Configuration JSON file")

    parser.add_argument(
        "--request-json",
        type=str,
        help="JSON file containing full API request information (model, messages, extra_body)",
    )

    parser.add_argument(
        "--api-key", type=str, help="DashScope API key (or set ALIYUN_API_KEY env var)"
    )

    parser.add_argument(
        "--source-lang",
        type=str,
        default="zh",
        help="Source language (default: zh, use 'auto' for detection)",
    )

    parser.add_argument(
        "--target-lang", type=str, default="en", help="Target language (default: en)"
    )

    parser.add_argument(
        "--domains",
        type=str,
        help="Domain description for translation style (default: general)",
    )

    parser.add_argument(
        "--model",
        type=str,
        default="qwen-mt-plus",
        help="Qwen MT model (default: qwen-mt-plus)",
    )

    # translation memory option removed

    parser.add_argument(
        "--chunk-tokens",
        type=int,
        default=3500,
        help="Target tokens per chunk (default: 3500)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    try:
        # Handle request from JSON file
        if args.request_json:
            request_path = Path(args.request_json)
            if not request_path.exists():
                print(
                    f"Error: Request JSON file '{args.request_json}' not found",
                    file=sys.stderr,
                )
                sys.exit(1)

            with open(request_path, "r", encoding="utf-8") as f:
                request_data = json.load(f)

            # Extract API key from config or args
            api_key = None
            if args.config:
                config = TranslatorConfig.from_json(args.config)
                api_key = config.api_key
            if not api_key and args.api_key:
                api_key = args.api_key
            if not api_key:
                api_key = TranslatorConfig().api_key  # Will raise if not set

            # Initialize OpenAI client
            client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            # Extract request parameters
            model = request_data.get("model", "qwen-mt-plus")
            messages = request_data.get("messages", [])
            extra_body = request_data.get("extra_body", {})
            stream = request_data.get("stream", False)

            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                extra_body=extra_body,
                stream=stream,
            )

            if stream:
                for chunk in response:
                    if chunk.choices:
                        content = chunk.choices[0].delta.content or ""
                        print(content, end="", flush=True)
                print()  # New line after streaming
            else:
                result = response.choices[0].message.content
                print(result)

            return

        # Original logic for text translation
        # Load configuration
        if args.config:
            config = TranslatorConfig.from_json(args.config)
            # Override with CLI args if provided
            if args.api_key:
                config.api_key = args.api_key
            if args.model:
                config.model = args.model
            if args.source_lang:
                config.source_lang = args.source_lang
            if args.target_lang:
                config.target_lang = args.target_lang
            if args.domains:
                config.domains = args.domains
        else:
            config = TranslatorConfig(
                api_key=args.api_key,
                model=args.model,
                source_lang=args.source_lang,
                target_lang=args.target_lang,
                domains=args.domains,
            )

        # Initialize translator
        translator = QwenMTTranslator(config)

        # Get input text
        if args.file:
            input_path = Path(args.file)
            if not input_path.exists():
                print(f"Error: Input file '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            text = input_path.read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            text = sys.stdin.read()

        # Translate
        result = translator.translate_text(text)

        # Output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(result["text"], encoding="utf-8")
            print(f"Translation saved to {args.output}")
            if args.debug:
                print(f"Token usage: {result['usage']}")
        else:
            print(result["text"])
            if args.debug:
                print(f"Token usage: {result['usage']}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
