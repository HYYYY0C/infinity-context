#!/usr/bin/env python3
"""
📋 一键复制当前对话

辅助脚本：帮助用户快速复制当前对话内容，用于生成摘要。

## 用法

```bash
# 方式 1: 直接运行（提示手动复制）
python scripts/copy_conversation.py

# 方式 2: 保存到文件
python scripts/copy_conversation.py --output conversation.txt

# 方式 3: 直接生成摘要
python scripts/copy_conversation.py --compress
```

## 注意

当前 Hermes Agent 未开放对话读取 API，因此需要手动复制。
未来版本将支持自动读取。
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime


def copy_conversation(output_file=None):
    """
    复制当前对话内容
    
    Args:
        output_file: 可选，保存到文件
    """
    print("="*70)
    print("📋 Infinity Context - 复制对话内容")
    print("="*70)
    print()
    print("⚠️  当前 Hermes 未开放对话读取 API")
    print()
    print("📝 请手动复制:")
    print("  1. 在 Hermes 界面中选中所有对话内容")
    print("  2. 复制 (Ctrl+C / Cmd+C)")
    print("  3. 粘贴到下方输入框")
    print()
    print("💡 提示:")
    print("  - 如果对话很长，可以分段复制")
    print("  - 只需复制关键部分（任务、决策、待办）")
    print()
    print("-"*70)
    
    # 等待用户输入
    try:
        conversation = input("\n请粘贴对话内容（或直接回车查看其他选项）: ").strip()
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        return None
    
    if not conversation:
        print()
        print("💡 你可以选择:")
        print("  1. 使用交互式模式（推荐）")
        print("     python -m src.cli compress --interactive")
        print()
        print("  2. 使用 LLM 自动生成（需提供对话）")
        print("     python -m src.cli compress --llm")
        print()
        print("  3. 查看使用指南")
        print("     cat docs/QUICKSTART.md")
        print()
        return None
    
    # 统计信息
    char_count = len(conversation)
    word_count = len(conversation.split())
    estimated_tokens = char_count // 4  # 粗略估算
    
    print()
    print("="*70)
    print("✅ 已接收对话内容")
    print("="*70)
    print(f"  字符数：{char_count:,}")
    print(f"  词数：{word_count:,}")
    print(f"  估算 Token: ~{estimated_tokens:,}")
    print()
    
    # 保存到文件（可选）
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(conversation, encoding='utf-8')
        print(f"💾 已保存到：{output_path.absolute()}")
        print()
    
    # 提供下一步建议
    print("🚀 下一步:")
    print()
    if output_file:
        print(f"  使用保存的文件生成摘要:")
        print(f"  python -m src.cli compress --input \"{conversation[:50]}...\"")
    else:
        print("  选项 A: 立即生成摘要（推荐）")
        print("  命令：python -m src.cli compress --llm")
        print()
        print("  选项 B: 交互式输入")
        print("  命令：python -m src.cli compress --interactive")
        print()
        print("  选项 C: 手动输入 JSON")
        print("  命令：python -m src.cli compress --input '{\"core_tasks\": [...]}'")
        print()
    
    return conversation


def compress_now(conversation: str):
    """
    立即生成摘要
    
    Args:
        conversation: 对话内容
    """
    print()
    print("="*70)
    print("🤖 正在调用 LLM 生成摘要...")
    print("="*70)
    print()
    print("⚠️  注意：此功能需要 Hermes Agent 环境")
    print()
    print("请在项目根目录运行:")
    print(f"  python -m src.cli compress --llm")
    print()
    print("然后粘贴你的对话内容。")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='📋 一键复制当前对话内容',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/copy_conversation.py              # 交互式复制
  python scripts/copy_conversation.py -o conv.txt  # 保存到文件
  python scripts/copy_conversation.py --compress   # 复制后生成摘要
        """
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='保存到文件'
    )
    
    parser.add_argument(
        '--compress',
        action='store_true',
        help='复制后立即生成摘要'
    )
    
    args = parser.parse_args()
    
    # 复制对话
    conversation = copy_conversation(args.output)
    
    if not conversation:
        return 0
    
    # 生成摘要（可选）
    if args.compress:
        compress_now(conversation)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
