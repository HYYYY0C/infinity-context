#!/usr/bin/env python3
"""
快速使用 LLM 摘要生成器

用法:
    python scripts/quick_summarize.py "对话内容..."
    
或者在 Python 中:
    from scripts.quick_summarize import summarize
    result = summarize("对话内容...")
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from hermes_tools import delegate_task
    
    def summarize(conversation: str, max_length: int = 400) -> dict:
        """
        使用当前 Hermes Agent 生成对话摘要
        
        Args:
            conversation: 对话文本
            max_length: 最大摘要长度
        
        Returns:
            结构化的摘要字典
        """
        prompt = f"""请为以下对话生成一个结构化的 JSON 摘要：

{conversation[:3000]}

请严格按照以下 JSON 格式输出（不要有其他文字）：
{{
  "summary": "一段话总结整个对话（100-200 字）",
  "key_points": ["关键点 1", "关键点 2", "关键点 3"],
  "action_items": ["待办事项 1", "待办事项 2"],
  "context": {{
    "项目": "...",
    "关键决策": "...",
    "技术栈": "..."
  }},
  "next_steps": "下一步建议（50-100 字）",
  "confidence": 0.95
}}
"""
        
        result = delegate_task(
            goal="生成对话摘要",
            context=prompt,
            role="leaf"
        )
        
        if result and len(result) > 0:
            return result[0]
        else:
            raise RuntimeError("摘要生成失败")
    
    def to_markdown(result: dict) -> str:
        """将摘要转换为 Markdown 格式"""
        md = []
        md.append("## 📝 Session 摘要\n")
        md.append(f"*置信度：{result.get('confidence', 0):.0%}*\n")
        
        md.append("### 📌 核心摘要\n")
        md.append(result.get('summary', '') + "\n")
        
        if result.get('key_points'):
            md.append("### 🔑 关键点\n")
            for point in result['key_points']:
                md.append(f"- {point}")
            md.append("")
        
        if result.get('action_items'):
            md.append("### ✅ 待办事项\n")
            for item in result['action_items']:
                md.append(f"- [ ] {item}")
            md.append("")
        
        if result.get('context'):
            md.append("### 📎 关键上下文\n")
            for key, value in result['context'].items():
                md.append(f"- **{key}**: {value}")
            md.append("")
        
        if result.get('next_steps'):
            md.append("### 🚀 下一步\n")
            md.append(result['next_steps'] + "\n")
        
        return "\n".join(md)
    
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("用法：python quick_summarize.py \"对话内容...\"")
            print("\n示例:")
            print('  python quick_summarize.py "User: 你好\\nAssistant: 你好！有什么可以帮助你的？"')
            sys.exit(1)
        
        conversation = " ".join(sys.argv[1:])
        
        print("⏳ 正在生成摘要...\n")
        result = summarize(conversation)
        
        print("\n✅ 摘要生成成功！\n")
        print(to_markdown(result))
        
except ImportError:
    print("❌ 不在 Hermes Agent 环境中")
    print("\n💡 提示:")
    print("  这个脚本需要在 Hermes Agent 会话中运行")
    print("  或者配置 OPENAI_API_KEY / ANTHROPIC_API_KEY")
    sys.exit(1)
