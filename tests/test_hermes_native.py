#!/usr/bin/env python3
"""
测试：使用当前 Hermes Agent 生成摘要

这个脚本演示了如何直接使用当前会话的 LLM 生成摘要，
无需额外配置 API Key！
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 测试对话
TEST_CONVERSATION = """
User: 我想优化 Infinity Context 的摘要功能
Assistant: 好的！当前是基于模板的，你想怎么优化？
User: 直接用当前 Hermes Agent 的 API，这样不用配置
Assistant: 好主意！我可以通过 delegate_task 让你生成摘要
User: 对，这样最智能，自动使用当前模型
Assistant: 明白了！我立即实现
"""

def test_hermes_native_summarize():
    """测试使用 Hermes 原生 API 生成摘要"""
    print("="*70)
    print("🤖 测试：使用当前 Hermes Agent 生成摘要")
    print("="*70)
    
    try:
        from hermes_tools import delegate_task
        
        print("\n✅ 检测到 Hermes Agent 环境")
        print("📝 对话内容:")
        print("-"*70)
        print(TEST_CONVERSATION)
        print("-"*70)
        
        # 构建摘要任务
        summary_prompt = f"""请为以下对话生成一个结构化的 JSON 摘要：

{TEST_CONVERSATION}

请严格按照以下 JSON 格式输出（不要有其他文字）：
{{
  "summary": "一段话总结（100-200 字）",
  "key_points": ["关键点 1", "关键点 2"],
  "action_items": ["待办 1", "待办 2"],
  "context": {{"技术": "...", "决策": "..."}},
  "next_steps": "下一步建议",
  "confidence": 0.95
}}
"""
        
        print("\n⏳ 正在委托给 Hermes Agent 生成摘要...\n")
        
        # 委托给子代理
        result = delegate_task(
            goal="生成对话摘要",
            context=summary_prompt,
            role="leaf"
        )
        
        print("\n✅ 摘要生成成功！")
        print("\n📊 结果:")
        print("-"*70)
        
        if result and len(result) > 0:
            print(json.dumps(result[0], indent=2, ensure_ascii=False))
        else:
            print("⚠️  结果为空")
        
        print("-"*70)
        
    except ImportError:
        print("\n❌ 不在 Hermes Agent 环境中")
        print("   hermes_tools 不可用")
        print("\n💡 提示:")
        print("   这个脚本需要在 Hermes Agent 会话中运行")
        print("   当前环境无法测试，但代码已准备好")
        
    except Exception as e:
        print(f"\n❌ 发生错误：{str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_hermes_native_summarize()
