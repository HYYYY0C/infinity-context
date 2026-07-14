#!/usr/bin/env python3
"""
LLM-Powered Smart Summarizer - 使用 LLM 自动生成智能摘要

相比基于模板的摘要，LLM 摘要的优势：
1. 更精炼 - 自动提取最关键信息
2. 更连贯 - 自然语言，易于理解
3. 更智能 - 识别隐含的上下文和依赖关系
4. 更灵活 - 适应不同类型的对话

用法:
    from src.llm_summarizer import LLMSummarizer
    
    summarizer = LLMSummarizer(model="gpt-3.5-turbo")
    summary = summarizer.generate(conversation_text, max_length=500)
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SummaryResult:
    """摘要结果"""
    summary_text: str
    key_points: List[str]
    action_items: List[str]
    context_items: Dict[str, str]
    next_steps: str  # 下一步建议
    confidence: float  # 0.0-1.0，置信度
    model_used: str
    tokens_used: int


class LLMSummarizer:
    """LLM 驱动的智能摘要生成器"""
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        max_length: int = 500,
        temperature: float = 0.3
    ):
        """
        初始化 LLM 摘要生成器
        
        Args:
            model: LLM 模型名称
            max_length: 最大摘要长度（字符）
            temperature: 温度参数（0.0-1.0，越低越确定）
        """
        self.model = model
        self.max_length = max_length
        self.temperature = temperature
        
        # 系统提示词 - 指导 LLM 如何生成摘要
        self.system_prompt = """你是一位专业的对话摘要专家。你的任务是从冗长的对话历史中提取最关键的信息，生成精炼、连贯的摘要。

## 要求

1. **精炼**: 只保留最重要的信息，去除冗余
2. **结构化**: 使用清晰的标题和列表
3. **可操作**: 明确指出待办事项和下一步
4. **上下文**: 保留关键的技术细节、决策和参数
5. **简洁**: 控制在 {max_length} 字以内

## 输出格式

请严格按照以下 JSON 格式输出：

```json
{{
  "summary": "一段话总结整个对话（100-200 字）",
  "key_points": ["关键点 1", "关键点 2", "关键点 3"],
  "action_items": ["待办事项 1", "待办事项 2"],
  "context": {{
    "技术栈": "使用的技术",
    "关键决策": "重要决定",
    "参数配置": "重要参数"
  }},
  "next_steps": "下一步建议（50-100 字）",
  "confidence": 0.95
}}
```

## 注意事项

- 如果某些信息不存在，对应字段留空或省略
- 技术术语保留原文（如函数名、类名、文件名）
- 数字和参数要准确
- 置信度反映你对摘要完整性的信心
"""

    def generate(
        self,
        conversation_text: str,
        custom_instructions: Optional[str] = None
    ) -> SummaryResult:
        """
        生成智能摘要
        
        Args:
            conversation_text: 对话历史文本
            custom_instructions: 自定义指令（可选）
        
        Returns:
            SummaryResult: 结构化的摘要结果
        """
        # 构建用户提示词
        user_prompt = self._build_user_prompt(
            conversation_text,
            custom_instructions
        )
        
        # 调用 LLM API
        llm_response = self._call_llm_api(user_prompt)
        
        # 解析响应
        result = self._parse_response(llm_response)
        
        return result
    
    def _build_user_prompt(
        self,
        conversation: str,
        custom_instructions: Optional[str] = None
    ) -> str:
        """构建用户提示词"""
        prompt = f"""请为以下对话历史生成摘要：

{'='*60}
{conversation[:10000]}  # 限制输入长度，避免超出 token 限制
{'='*60}
"""
        
        if custom_instructions:
            prompt += f"\n\n额外要求：\n{custom_instructions}"
        
        prompt += f"\n\n请生成不超过 {self.max_length} 字的摘要。"
        
        return prompt
    
    def _call_llm_api(self, user_prompt: str) -> str:
        """
        调用 LLM API
        
        自动检测并使用可用的 API（优先级从高到低）：
        1. 使用当前 Hermes Agent 的 API（如果可用）
        2. 如果有 OPENAI_API_KEY，使用 OpenAI
        3. 如果有 ANTHROPIC_API_KEY，使用 Anthropic
        4. 如果本地有 Ollama，使用 Ollama
        5. 否则使用模拟响应（测试用）
        """
        import os
        
        # 方案 0: 尝试使用当前 Hermes Agent 的 API
        # 通过调用 Hermes 的工具来生成摘要
        try:
            print("💡 尝试使用当前 Hermes Agent 的 API...")
            return self._call_hermes_agent(user_prompt)
        except Exception as e:
            print(f"⚠️  Hermes Agent API 不可用：{str(e)}")
            print("   尝试其他 API...\n")
        
        # 方案 1: 检测 OpenAI API Key
        if os.getenv("OPENAI_API_KEY"):
            print("💡 检测到 OpenAI API Key，使用 OpenAI API...")
            try:
                return self._call_openai(user_prompt)
            except Exception as e:
                print(f"⚠️  OpenAI API 调用失败：{str(e)}")
                print("   回退到模拟响应...\n")
        
        # 方案 2: 检测 Anthropic API Key
        elif os.getenv("ANTHROPIC_API_KEY"):
            print("💡 检测到 Anthropic API Key，使用 Anthropic API...")
            try:
                return self._call_anthropic(user_prompt)
            except Exception as e:
                print(f"⚠️  Anthropic API 调用失败：{str(e)}")
                print("   回退到模拟响应...\n")
        
        # 方案 3: 检测本地 Ollama
        else:
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    print("💡 检测到本地 Ollama，使用 Ollama API...")
                    return self._call_ollama(user_prompt)
            except:
                pass
        
        # 方案 4: 模拟响应（测试用）
        print("💡 未检测到 API 配置，使用模拟响应（测试模式）")
        print("   配置 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 以启用真实 LLM\n")
        return self._mock_response()
    
    def _call_hermes_agent(self, user_prompt: str) -> str:
        """
        通过 delegate_task 让当前 Hermes Agent 生成摘要
        
        这是最智能的方式：直接使用当前会话的模型和 API
        无需额外配置，自动继承 Hermes 的设置
        
        注意：这个方法需要在 Hermes Agent 环境中运行
        """
        try:
            # 尝试导入 delegate_task
            from hermes_tools import delegate_task
            
            print("   🤖 委托给当前 Hermes Agent 生成摘要...")
            
            # 构建摘要任务
            summary_prompt = f"""请为以下对话生成一个结构化的 JSON 摘要：

{user_prompt[:3000]}

请严格按照以下 JSON 格式输出（不要有其他文字）：
{{
  "summary": "一段话总结（100-200 字）",
  "key_points": ["关键点 1", "关键点 2", "关键点 3"],
  "action_items": ["待办 1", "待办 2"],
  "context": {{"技术": "...", "决策": "..."}},
  "next_steps": "下一步建议（50-100 字）",
  "confidence": 0.95
}}
"""
            
            # 委托给子代理（使用当前模型）
            result = delegate_task(
                goal="生成对话摘要",
                context=summary_prompt,
                role="leaf"
            )
            
            # 等待结果（delegate_task 是同步的）
            if result and len(result) > 0:
                # 提取摘要文本
                summary_text = result[0].get("summary", "")
                if summary_text:
                    # 构建完整的 JSON 响应
                    return json.dumps({
                        "summary": summary_text,
                        "key_points": result[0].get("key_points", []),
                        "action_items": result[0].get("action_items", []),
                        "context": result[0].get("context", {}),
                        "next_steps": result[0].get("next_steps", ""),
                        "confidence": result[0].get("confidence", 0.9)
                    }, ensure_ascii=False)
            
            raise RuntimeError("delegate_task 返回为空")
            
        except ImportError:
            raise RuntimeError("不在 Hermes Agent 环境中（hermes_tools 不可用）")
        except Exception as e:
            raise RuntimeError(f"delegate_task 调用失败：{str(e)}")
    
    def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt.format(
                        max_length=self.max_length
                    )},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API 调用失败：{str(e)}")
    
    def _call_anthropic(self, prompt: str) -> str:
        """调用 Anthropic API"""
        try:
            from anthropic import Anthropic
            import os
            
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            response = client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt.format(max_length=self.max_length),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API 调用失败：{str(e)}")
    
    def _call_ollama(self, prompt: str) -> str:
        """调用本地 Ollama 模型"""
        try:
            import requests
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature
                    }
                }
            )
            
            return response.json()["response"]
            
        except Exception as e:
            raise RuntimeError(f"Ollama 调用失败：{str(e)}")
    
    def _mock_response(self) -> str:
        """示例响应（用于测试）"""
        return json.dumps({
            "summary": "本次对话主要讨论了 Infinity Context 项目的优化工作。用户决定改进摘要生成算法，使用 LLM 替代基于模板的方法，以提升摘要的智能性和连贯性。",
            "key_points": [
                "当前摘要基于模板，缺乏灵活性",
                "LLM 可以生成更精炼、更智能的摘要",
                "需要支持多种 LLM 后端（OpenAI/Anthropic/Ollama）"
            ],
            "action_items": [
                "实现 LLM 摘要生成器",
                "添加多种 API 支持",
                "编写单元测试"
            ],
            "context": {
                "技术栈": "Python, Click, OpenAI API",
                "关键决策": "支持多后端，优先实现 OpenAI",
                "项目": "Infinity Context v0.3.0"
            },
            "next_steps": "接下来将实现 LLM 摘要生成器，首先完成 OpenAI API 集成，然后添加 Anthropic 和本地模型支持。同时需要编写文档说明配置方法。",
            "confidence": 0.95
        }, ensure_ascii=False)
    
    def _parse_response(self, response_text: str) -> SummaryResult:
        """解析 LLM 响应"""
        try:
            # 尝试解析 JSON
            data = json.loads(response_text)
            
            return SummaryResult(
                summary_text=data.get("summary", ""),
                key_points=data.get("key_points", []),
                action_items=data.get("action_items", []),
                context_items=data.get("context", {}),
                next_steps=data.get("next_steps", ""),
                confidence=data.get("confidence", 0.0),
                model_used=self.model,
                tokens_used=self._estimate_tokens(response_text)
            )
            
        except json.JSONDecodeError as e:
            # 如果解析失败，尝试从文本中提取
            raise ValueError(f"LLM 响应格式错误：{str(e)}\n响应内容：{response_text[:500]}")
    
    def _estimate_tokens(self, text: str) -> int:
        """估算 token 数量"""
        # 简单估算：4 字符 ≈ 1 token
        return len(text) // 4
    
    def generate_markdown(self, result: SummaryResult) -> str:
        """将摘要结果转换为 Markdown 格式"""
        md = []
        md.append("## 📝 Session 摘要\n")
        md.append(f"*生成时间：{__import__('datetime').datetime.now().isoformat()}*\n")
        md.append(f"*使用模型：{result.model_used}*\n")
        md.append(f"*置信度：{result.confidence:.0%}*\n")
        
        md.append("### 📌 核心摘要\n")
        md.append(result.summary_text + "\n")
        
        if result.key_points:
            md.append("### 🔑 关键点\n")
            for point in result.key_points:
                md.append(f"- {point}")
            md.append("\n")
        
        if result.action_items:
            md.append("### ✅ 待办事项\n")
            for item in result.action_items:
                md.append(f"- [ ] {item}")
            md.append("\n")
        
        if result.context_items:
            md.append("### 📎 关键上下文\n")
            for key, value in result.context_items.items():
                md.append(f"- **{key}**: {value}")
            md.append("\n")
        
        if result.next_steps:
            md.append("### 🚀 下一步\n")
            md.append(result.next_steps + "\n")
        
        return "\n".join(md)


# 便捷函数
def quick_summarize(
    conversation: str,
    model: str = "gpt-3.5-turbo",
    max_length: int = 500
) -> str:
    """
    快速生成摘要
    
    Args:
        conversation: 对话文本
        model: 模型名称
        max_length: 最大长度
    
    Returns:
        Markdown 格式的摘要
    """
    summarizer = LLMSummarizer(model=model, max_length=max_length)
    result = summarizer.generate(conversation)
    return summarizer.generate_markdown(result)


# CLI 入口
if __name__ == "__main__":
    # 测试示例
    test_conversation = """
    User: 我想优化 Infinity Context 项目的摘要生成算法
    Assistant: 好的！当前的摘要是基于模板的，你想怎么优化？
    User: 用 LLM 自动生成更智能的摘要
    Assistant: 明白了！我会创建一个使用 LLM 的摘要生成器...
    """
    
    result = quick_summarize(test_conversation)
    print(result)
