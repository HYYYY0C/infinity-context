#!/usr/bin/env python3
"""
🔄 Infinity Context v1.0.0 - 极简版

**唯一目标**: 小模型，长上下文
"""

import sys
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hermes_tools import session_search, terminal, send_message, computer_use
else:
    try:
        from hermes_tools import session_search, terminal, send_message, computer_use
    except ImportError:
        session_search = None
        terminal = None
        send_message = None
        computer_use = None


def check_and_rotate():
    """检查并自动切换 - 极简版"""
    
    if session_search is None:
        print("❌ 请在 Hermes 环境中运行")
        return
    
    print("🔄 Infinity Context - 自动检查")
    
    try:
        recent = session_search(limit=1)
        messages = session_search(session_id=recent.id, window=100)
    except Exception as e:
        print(f"❌ 无法读取会话：{e}")
        return
    
    total_tokens = sum(len(m.get('content', '')) for m in messages) // 4
    usage_rate = total_tokens / 128000
    
    print(f"📊 使用率：{usage_rate:.1%} ({total_tokens:,} tokens)")
    
    if usage_rate < 0.8:
        print("✅ 使用率正常")
        return
    
    print("⚠️  使用率超过 80%，执行切换...")
    print("📝 生成摘要...")
    summary_text = f"会话摘要：共 {len(messages)} 轮对话。"
    
    print("✍️  执行 /new...")
    try:
        computer_use.click_element("输入框")
        computer_use.type_text("/new")
        computer_use.press_key("Enter")
        time.sleep(2)
        print("✅ 已执行 /new")
    except Exception as e:
        print(f"❌ 执行失败：{e}")
        print("💡 请手动执行：/new")
        return
    
    print("💉 注入摘要...")
    send_message(f"📋 **已自动恢复上下文**\n\n{summary_text}\n\n我们可以继续了！")
    
    print("✅ 切换完成")


if __name__ == "__main__":
    check_and_rotate()
