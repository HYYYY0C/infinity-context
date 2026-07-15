#!/usr/bin/env python3
"""
🔄 Infinity Context v1.1.0 - 支持小模型

**目标**: 小模型，长上下文

自动检测模型并调整 Context 限制，支持从 4K 到 200K 的所有模型！
"""

import sys
import os
import time
import tiktoken
import json
import re
from typing import Dict, List
from pathlib import Path

# 条件导入 Hermes 工具
if sys.modules.get('hermes_tools'):
    from hermes_tools import session_search, send_message, computer_use, delegate_task
else:
    try:
        from hermes_tools import session_search, send_message, computer_use, delegate_task
    except ImportError:
        session_search = None
        send_message = None
        computer_use = None
        delegate_task = None

# ========== 模型配置 ==========
MODEL_CONFIGS: Dict[str, Dict] = {
    # OpenAI
    "gpt-3.5-turbo": {"limit": 16385, "encoding": "cl100k_base"},
    "gpt-4-turbo": {"limit": 128000, "encoding": "cl100k_base"},
    "gpt-4o": {"limit": 128000, "encoding": "cl100k_base"},
    
    # Anthropic
    "claude-3-haiku": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-sonnet": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-opus": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-sonnet-4": {"limit": 200000, "encoding": "cl100k_base"},
    
    # Meta Llama
    "llama-3-8b": {"limit": 8192, "encoding": "cl100k_base"},       # Llama-3 (8K)
    "llama-3-70b": {"limit": 8192, "encoding": "cl100k_base"},      # Llama-3 (8K)
    "llama-3.1-8b": {"limit": 128000, "encoding": "cl100k_base"},   # Llama-3.1 (128K)
    "llama-3.1-70b": {"limit": 128000, "encoding": "cl100k_base"},  # Llama-3.1 (128K)
    
    # Mistral
    "mistral-7b": {"limit": 8192, "encoding": "cl100k_base"},
    "mistral-medium": {"limit": 32000, "encoding": "cl100k_base"},
    
    # Microsoft Phi
    "phi-3-mini": {"limit": 4096, "encoding": "cl100k_base"},
    "phi-3-medium": {"limit": 128000, "encoding": "cl100k_base"},
    
    # 默认
    "default": {"limit": 128000, "encoding": "cl100k_base"},
}

def get_model_config(model_name: str) -> Dict:
    """获取模型配置"""
    # 不要替换 - 和 . ，直接用小写匹配
    normalized = model_name.lower()
    
    # 1. 精确匹配
    if normalized in MODEL_CONFIGS:
        return MODEL_CONFIGS[normalized]
    
    # 2. 检查是否包含已知模型的关键词
    for key, config in MODEL_CONFIGS.items():
        if key == "default":  # 跳过默认值
            continue
        if key in normalized or normalized in key:
            return config
    
    # 3. 返回默认
    return MODEL_CONFIGS["default"]


def check_and_rotate():
    """检查并自动切换 - 支持小模型"""
    
    if session_search is None:
        print("❌ 请在 Hermes 环境中运行")
        return
    
    # 1. 获取当前模型
    model_name = os.getenv("LLM_MODEL", "claude-sonnet-4")
    config = get_model_config(model_name)
    
    TOKEN_LIMIT = config["limit"]
    ENCODING = config["encoding"]
    
    print(f"🔄 Infinity Context v1.1.0 - 自动检查")
    print(f"📊 使用模型：{model_name}")
    print(f"   Context 限制：{TOKEN_LIMIT:,} tokens")
    
    # 2. 动态调整阈值（Hermes 最小支持 64K，以下为小模型）
    if TOKEN_LIMIT < 64000:  # <64K 算小模型（Hermes 原生不支持）
        USAGE_THRESHOLD = 0.7  # 小模型：70%
        RECENT_MESSAGES = 10   # 只保留最近 10 轮
        print(f"   触发阈值：70% ({TOKEN_LIMIT * 0.7:,.0f} tokens)")
        print(f"   🐜 小模型模式：启用（Hermes 原生不支持）")
    else:
        USAGE_THRESHOLD = 0.8  # 大模型：80%
        RECENT_MESSAGES = 50
        print(f"   触发阈值：80% ({TOKEN_LIMIT * 0.8:,.0f} tokens)")
    
    # 3. 获取会话
    try:
        # session_search 返回 {"sessions": [...]} 格式
        search_result = session_search(limit=1)
        
        # 检查是否有会话
        if not search_result.get("sessions"):
            print("❌ 无法读取会话：无会话数据")
            return
        
        # 获取第一个会话的 ID
        current_session_id = search_result["sessions"][0].get("id") or search_result["sessions"][0].get("session_id")
        
        if not current_session_id:
            print("❌ 无法获取会话 ID")
            return
        
        # 使用 session_id 读取消息（不能用 window，要用 around_message_id）
        # 先读取最近的消息来获取上下文
        messages_result = session_search(session_id=current_session_id)
        
        # messages_result 可能是 {"messages": [...]} 或直接是消息列表
        if isinstance(messages_result, dict):
            messages = messages_result.get("messages", [])
        elif isinstance(messages_result, list):
            messages = messages_result
        else:
            print(f"❌ 意外的消息格式：{type(messages_result)}")
            return
        
        if not messages:
            print("❌ 会话中没有消息")
            return
            
    except Exception as e:
        print(f"❌ 无法读取会话：{e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. 计算 Token
    try:
        encoding = tiktoken.get_encoding(ENCODING)
        total_tokens = sum(len(encoding.encode(m.get('content', ''))) for m in messages)
    except ImportError:
        print("⚠️  tiktoken 未安装，使用估算（误差较大）")
        total_tokens = sum(len(m.get('content', '')) for m in messages) // 4
    except Exception as e:
        print(f"⚠️  Token 计算失败：{e}")
        total_tokens = sum(len(m.get('content', '')) for m in messages) // 4
    
    usage_rate = total_tokens / TOKEN_LIMIT
    
    print(f"📈 当前使用：{total_tokens:,} tokens ({usage_rate:.1%})")
    
    # 5. 检查阈值
    if usage_rate < USAGE_THRESHOLD:
        print("✅ 使用率正常")
        return
    
    print(f"⚠️  使用率超过 {USAGE_THRESHOLD:.0%}，执行切换...")
    
    # 6. 生成摘要（根据模型大小调整）
    print("📝 生成摘要...")
    try:
        # 提取最近对话
        recent = messages[-RECENT_MESSAGES:]
        conversation = "\n".join([f"{m.get('role', 'unknown')}: {m.get('content', '')}" for m in recent])
        
        # 根据模型大小调整摘要复杂度
        if TOKEN_LIMIT < 32000:
            # 小模型：精简摘要
            goal = "提取 3 个关键点，50 字以内"
        else:
            # 大模型：结构化摘要
            goal = "生成结构化摘要（JSON 格式），包含 summary, key_points, action_items"
        
        result = delegate_task(
            goal=goal,
            context=f"分析以下对话：\n\n{conversation[:20000]}"
        )
        
        # 解析 JSON（如果是结构化摘要）
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match and TOKEN_LIMIT >= 32000:
            try:
                summary_data = json.loads(json_match.group())
                summary_text = summary_data.get('summary', '摘要生成成功')
                key_points = summary_data.get('key_points', [])
                action_items = summary_data.get('action_items', [])
                
                summary_text = f"""
**摘要**: {summary_text}

**关键点**:
{chr(10).join('• ' + str(p) for p in key_points[:5])}

**待办**:
{chr(10).join('• ' + str(t) for t in action_items[:5])}
""".strip()
            except:
                summary_text = result
        else:
            # 小模型或解析失败：使用原始结果
            summary_text = result
            
    except Exception as e:
        print(f"⚠️  摘要生成失败：{e}")
        summary_text = f"会话摘要：共 {len(messages)} 轮对话（降级模式）"
    
    # 7. 执行 /new
    print("✍️  执行 /new...")
    
    # 检测 Computer Use 是否可用
    computer_use_available = (
        computer_use is not None and 
        hasattr(computer_use, 'browser_snapshot') and
        hasattr(computer_use, 'browser_click') and
        hasattr(computer_use, 'browser_type') and
        hasattr(computer_use, 'browser_press')
    )
    
    if computer_use_available:
        try:
            # 获取页面快照找到输入框
            from hermes_tools import browser_snapshot, browser_click, browser_type, browser_press
            
            snapshot = browser_snapshot()
            # 查找输入框的 ref ID（通常是最后一个可输入元素）
            # 这里简化处理，实际需要根据快照解析
            print("⚠️  Computer Use 功能需要实现输入框定位逻辑")
            print("💡 暂时请手动执行：/new")
            
            # TODO: 实现完整的 Computer Use 流程
            # snapshot = browser_snapshot()
            # 解析 snapshot 找到输入框的 ref ID
            # browser_type(ref="@eX", text="/new")
            # browser_press(key="Enter")
            
        except Exception as e:
            print(f"❌ Computer Use 执行失败：{e}")
            print("💡 请手动执行：/new")
    else:
        print("⚠️  Computer Use 不可用（Cron 环境限制）")
        print("💡 请手动执行：/new")
    
    # 发送提醒消息
    try:
        send_message(f"""
⚠️  **会话使用率超过 {USAGE_THRESHOLD:.0%}，建议切换新会话**

📋 **摘要**：
{summary_text[:500]}...

💡 **请执行**：`/new` 开始新会话，然后说"继续"
""")
        print("✅ 已发送提醒消息")
    except Exception as e:
        print(f"❌ 发送消息失败：{e}")


if __name__ == "__main__":
    check_and_rotate()
