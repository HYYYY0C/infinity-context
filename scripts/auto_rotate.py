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
    # 使用 tiktoken 准确计算 Token
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        total_tokens = sum(len(encoding.encode(m.get('content', ''))) for m in messages)
    except ImportError:
        print("⚠️  tiktoken 未安装，使用估算（误差较大）")
        total_tokens = sum(len(m.get('content', '')) for m in messages) // 4
    except Exception as e:
        print(f"⚠️  Token 计算失败：{e}")
        total_tokens = sum(len(m.get('content', '')) for m in messages) // 4
    
    usage_rate = total_tokens / 128000
    
    print(f"📊 使用率：{usage_rate:.1%} ({total_tokens:,} tokens)")
    
    if usage_rate < 0.8:
        print("✅ 使用率正常")
        return
    
    print("⚠️  使用率超过 80%，执行切换...")
    
    # 生成真正的 LLM 摘要
    print("📝 生成摘要...")
    try:
        from hermes_tools import delegate_task
        import json, re
        
        # 提取最近 50 轮对话
        recent = messages[-50:]
        conversation = "\n".join([f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in recent])
        
        # 调用 LLM 生成结构化摘要
        result = delegate_task(
            goal="生成结构化摘要（JSON 格式）",
            context=f"分析以下对话，提取关键信息：\n\n{conversation[:20000]}"
        )
        
        # 解析 JSON
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group())
            summary_text = summary_data.get('summary', '摘要生成成功')
            key_points = summary_data.get('key_points', [])
            action_items = summary_data.get('action_items', [])
            
            # 格式化摘要
            summary_text = f"""
**摘要**: {summary_text}

**关键点**:
{chr(10).join('• ' + str(p) for p in key_points[:5])}

**待办**:
{chr(10).join('• ' + str(t) for t in action_items[:5])}
""".strip()
        else:
            summary_text = f"会话摘要：共 {len(messages)} 轮对话（LLM 解析失败）"
    except Exception as e:
        print(f"⚠️  摘要生成失败：{e}")
        summary_text = f"会话摘要：共 {len(messages)} 轮对话（降级模式）"
    
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
