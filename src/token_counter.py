#!/usr/bin/env python3
"""
Token Counter - 准确的 token 计数工具

使用 tiktoken 库进行精确的 token 计数，支持多种模型
"""

import tiktoken
from typing import Dict, List, Optional


class TokenCounter:
    """Token 计数器"""
    
    # 常见模型的 encoding 映射
    MODEL_ENCODINGS = {
        # OpenAI / Codex
        "gpt-4": "cl100k_base",
        "gpt-4o": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "codex": "cl100k_base",
        
        # Anthropic
        "claude-3": "cl100k_base",  # Claude 使用与 GPT-4 相同的 encoding
        "claude-sonnet": "cl100k_base",
        "claude-opus": "cl100k_base",
        
        # 默认
        "default": "cl100k_base",
    }
    
    def __init__(self, model: str = "default"):
        """
        初始化 Token 计数器
        
        Args:
            model: 模型名称，用于选择正确的 encoding
        """
        self.model = model
        self.encoding_name = self.MODEL_ENCODINGS.get(model, "cl100k_base")
        
        try:
            self.encoding = tiktoken.get_encoding(self.encoding_name)
        except Exception:
            # 如果 encoding 不存在，回退到默认
            self.encoding_name = "cl100k_base"
            self.encoding = tiktoken.get_encoding(self.encoding_name)
    
    def count_text(self, text: str) -> int:
        """
        计算文本的 token 数
        
        Args:
            text: 要计算的文本
            
        Returns:
            token 数量
        """
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def count_messages(self, messages: List[Dict]) -> int:
        """
        计算对话消息列表的 token 数
        
        Args:
            messages: 对话消息列表，格式为 [{"role": "user", "content": "..."}, ...]
            
        Returns:
            总 token 数
        """
        total_tokens = 0
        
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            # 计算内容 token
            total_tokens += self.count_text(content)
            
            # 计算 role token (通常很少，但为了准确也计算)
            total_tokens += self.count_text(role)
        
        return total_tokens
    
    def count_with_tools(self, messages: List[Dict], tool_outputs: Optional[List[str]] = None) -> int:
        """
        计算包含工具输出的对话 token 数
        
        Args:
            messages: 对话消息列表
            tool_outputs: 工具输出列表（可选）
            
        Returns:
            总 token 数
        """
        total = self.count_messages(messages)
        
        if tool_outputs:
            for output in tool_outputs:
                total += self.count_text(output)
        
        return total
    
    def estimate_from_length(self, char_length: int) -> int:
        """
        根据字符长度粗略估算 token 数
        
        英文：1 token ≈ 4 字符
        中文：1 token ≈ 1.5 字符
        
        Args:
            char_length: 字符长度
            
        Returns:
            估算的 token 数
        """
        # 简单估算：假设中英文混合，1 token ≈ 2.5 字符
        return int(char_length / 2.5)
    
    def get_model_info(self) -> Dict:
        """
        获取当前模型信息
        
        Returns:
            模型信息字典
        """
        return {
            "model": self.model,
            "encoding": self.encoding_name,
            "vocab_size": self.encoding.n_vocab,
        }


def quick_count(text: str, model: str = "default") -> int:
    """
    快速计算文本 token 数的便捷函数
    
    Args:
        text: 要计算的文本
        model: 模型名称
        
    Returns:
        token 数量
    """
    counter = TokenCounter(model=model)
    return counter.count_text(text)


def main():
    """测试 Token 计数器"""
    print("=" * 80)
    print("🔢 Token Counter - 测试")
    print("=" * 80)
    print()
    
    # 测试 1: 简单文本
    test_text = "Hello, world! 你好，世界！"
    counter = TokenCounter(model="gpt-4")
    tokens = counter.count_text(test_text)
    
    print(f"测试 1: 简单文本")
    print(f"  文本：{test_text}")
    print(f"  字符数：{len(test_text)}")
    print(f"  Token 数：{tokens}")
    print(f"  模型：{counter.model} ({counter.encoding_name})")
    print()
    
    # 测试 2: 对话消息
    test_messages = [
        {"role": "user", "content": "你好，请帮我写个 Python 脚本"},
        {"role": "assistant", "content": "好的，请问需要什么功能的脚本？"},
        {"role": "user", "content": "需要一个文件批量重命名的脚本"},
    ]
    
    total = counter.count_messages(test_messages)
    print(f"测试 2: 对话消息")
    print(f"  消息数：{len(test_messages)}")
    print(f"  总 Token 数：{total}")
    print(f"  平均每消息：{total // len(test_messages):.0f} tokens")
    print()
    
    # 测试 3: 模型对比
    print("测试 3: 不同模型对比")
    models = ["gpt-4", "claude-sonnet", "default"]
    for model in models:
        c = TokenCounter(model=model)
        t = c.count_text(test_text)
        print(f"  {model:20s}: {t:4d} tokens (encoding: {c.encoding_name})")
    print()
    
    # 测试 4: 长文本
    long_text = "这是一个测试文本。" * 100
    tokens = counter.count_text(long_text)
    print(f"测试 4: 长文本")
    print(f"  字符数：{len(long_text)}")
    print(f"  Token 数：{tokens}")
    print(f"  字符/Token 比率：{len(long_text) / tokens:.2f}")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
