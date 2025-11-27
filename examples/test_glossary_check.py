#!/usr/bin/env python3
"""
Control-var test for glossary/header behavior.
Uses the same config but two different texts (short vs long) to see whether the API echoes a glossary/header.
"""
import os
from pathlib import Path
import textwrap

# Ensure submodule package import path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from qwen_mt_translator import TranslatorConfig, QwenMTTranslator


def detect_glossary_header(text: str) -> bool:
    """Detect if the API response includes a glossary/header JSON or domain preface.

    Heuristic: if within the first 500 chars there is a JSON-like entry with keys 'src' or 'tgt',
    or the domain sentence appears as a prefix, we consider it a glossary/header.
    """
    if not text:
        return False
    head = text[:1000]
    if '"src"' in head or '"tgt"' in head or '{"src"' in head:
        return True
    # also check for the 'I've included' sentence we observed
    if "I've included some words" in head or "I've included some words" in text:
        return True
    return False


def run_test():
    cfg_path = Path(__file__).parent.parent / "config" / "ranobe_config.json"
    config = TranslatorConfig.from_json(str(cfg_path))
    if not config.api_key:
        config.api_key = os.getenv("ALIYUN_API_KEY")
        if not config.api_key:
            print("SKIP: ALIYUN_API_KEY not set. Set it to run this live test.")
            return

    translator = QwenMTTranslator(config)

    # Short text (README-like)
    short_text = """# Project Name

This is a sample project for demonstrating translation features."""

    # Long text: prefer a bundled demo file inside the submodule; if missing, fall back
    # to a repeated-sentence long text. This removes dependency on the main project data.
    demo_long_file = Path(__file__).parent / "data" / "sample_long.md"
    if demo_long_file.exists():
        long_text = demo_long_file.read_text(encoding="utf-8")
    else:
        long_text = "这是一段用于模拟长文本的示例句子。" * 500

    print("Running control-var test with same config...")

    print("\n--- Short text translation (README-like) ---")
    try:
        short_res = translator.translate_text(short_text, use_memory=False)
        has_glossary_short = detect_glossary_header(short_res)
        print("Has glossary/header in short response:", has_glossary_short)
        print("\nShort response preview:\n", short_res[:800])
    except Exception as e:
        print("Short translation failed:", e)
        return

    print("\n--- Long text translation (novel-like) ---")
    try:
        long_res = translator.translate_text(long_text, use_memory=False)
        has_glossary_long = detect_glossary_header(long_res)
        print("Has glossary/header in long response:", has_glossary_long)
        print("\nLong response preview:\n", long_res[:800])
    except Exception as e:
        print("Long translation failed:", e)
        return

    print("\n=== Test Result Summary ===")
    print(f"Short text produced glossary/header: {has_glossary_short}")
    print(f"Long text produced glossary/header:  {has_glossary_long}")

    if has_glossary_short and not has_glossary_long:
        print(
            "\nOutcome: matches hypothesis — short (doc) requests produce glossary header while long (novel) do not."
        )
    else:
        print(
            "\nOutcome: DID NOT match hypothesis — observed behavior differs. Review outputs above."
        )


if __name__ == "__main__":
    run_test()
