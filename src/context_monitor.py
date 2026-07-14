#!/usr/bin/env python3
"""
Context Monitor - 监控 Hermes session 的 context 使用量

使用 tiktoken 进行准确的 token 计数，支持多种模型
"""

import os
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

try:
    from .token_counter import TokenCounter
    TOKEN_COUNTER_AVAILABLE = True
except ImportError:
    TOKEN_COUNTER_AVAILABLE = False


class ContextMonitor:
    """Hermes Session Context 监控器"""
    
    def __init__(self, threshold: float = 0.8, model_limit: int = 128000, model: str = "gpt-4"):
        """
        初始化监控器
        
        Args:
            threshold: 触发压缩的阈值（0.0-1.0），默认 80%
            model_limit: 模型 context 限制，默认 128K tokens
            model: 模型名称，用于选择正确的 encoding
        """
        self.threshold = threshold
        self.model_limit = model_limit
        self.model = model
        
        # 初始化 token 计数器
        if TOKEN_COUNTER_AVAILABLE:
            self.counter: Optional[TokenCounter] = TokenCounter(model=model)
        else:
            self.counter = None
            print("⚠️  tiktoken 未安装，使用粗略估算（每条消息 200 tokens）")
            print("   安装：pip install tiktoken")
    
    def estimate_from_message_count(self, message_count: int, avg_tokens_per_message: int = 200) -> Dict:
        """
        从消息数量估算 token 使用量（粗略方法）
        
        Args:
            message_count: 消息总数
            avg_tokens_per_message: 每条消息的平均 token 数
            
        Returns:
            包含估算结果的字典
        """
        estimated_tokens = message_count * avg_tokens_per_message
        usage_ratio = estimated_tokens / self.model_limit
        
        return {
            "message_count": message_count,
            "estimated_tokens": estimated_tokens,
            "model_limit": self.model_limit,
            "usage_ratio": usage_ratio,
            "threshold": self.threshold,
            "should_rotate": usage_ratio >= self.threshold,
            "status": self._get_status(usage_ratio),
            "method": "rough_estimate"
        }
    
    def count_tokens_accurate(self, messages: List[Dict]) -> Dict:
        """
        准确计算 token 使用量（使用 tiktoken）
        
        Args:
            messages: 对话消息列表 [{"role": "user", "content": "..."}, ...]
            
        Returns:
            包含准确结果的字典
        """
        if not self.counter:
            # 回退到粗略估算
            message_count = len(messages)
            return self.estimate_from_message_count(message_count)
        
        total_tokens = self.counter.count_messages(messages)
        usage_ratio = total_tokens / self.model_limit
        
        return {
            "message_count": len(messages),
            "estimated_tokens": total_tokens,
            "model_limit": self.model_limit,
            "usage_ratio": usage_ratio,
            "threshold": self.threshold,
            "should_rotate": usage_ratio >= self.threshold,
            "status": self._get_status(usage_ratio),
            "method": "accurate_count",
            "model": self.model,
            "encoding": self.counter.encoding_name
        }
    
    def detect_truncation(self, text: str) -> bool:
        """
        检测文本是否有截断标记
        
        Args:
            text: 要检测的文本
            
        Returns:
            True 如果检测到截断
        """
        truncation_markers = [
            "...[truncated]",
            "...[内容已截断]",
            "[输出过长，已截断]",
            "output truncated",
        ]
        
        text_lower = text.lower()
        return any(marker in text_lower for marker in truncation_markers)
    
    def _get_status(self, usage_ratio: float) -> str:
        """获取状态描述"""
        if usage_ratio >= 0.95:
            return "🔴 紧急（超过 95%）"
        elif usage_ratio >= self.threshold:
            return "🟠 警告（建议压缩）"
        elif usage_ratio >= 0.5:
            return "🟡 正常"
        else:
            return "🟢 健康"
    
    def quick_check(self) -> Dict:
        """
        快速检查（无需访问 Hermes API）
        
        Returns:
            检查结果字典
        """
        print("\n📊 Context 使用量快速检查")
        print("=" * 60)
        
        if self.counter:
            print(f"✅ 使用 tiktoken 准确计数 (模型：{self.model})")
        else:
            print("⚠️  使用粗略估算（每条消息 200 tokens）")
        
        print()
        
        try:
            message_count = int(input("当前对话大约多少轮？（估算即可）: "))
        except (ValueError, EOFError):
            message_count = 50  # 默认值
        
        result = self.estimate_from_message_count(message_count)
        
        print(f"\n估算结果:")
        print(f"  消息数：{result['message_count']}")
        print(f"  估算 token: {result['estimated_tokens']:,}")
        print(f"  使用率：{result['usage_ratio']*100:.1f}%")
        print(f"  状态：{result['status']}")
        
        if result['should_rotate']:
            print(f"\n💡 建议：使用 'hermes-rotator compress' 压缩对话")
        
        return result


def main():
    """测试 Context Monitor"""
    print("=" * 80)
    print("📊 Context Monitor - 测试")
    print("=" * 80)
    print()
    
    # 测试 1: 粗略估算
    print("测试 1: 粗略估算")
    print("-" * 60)
    monitor = ContextMonitor(threshold=0.8, model_limit=128000)
    result = monitor.estimate_from_message_count(60)
    print(f"  消息数：{result['message_count']}")
    print(f"  估算 token: {result['estimated_tokens']:,}")
    print(f"  使用率：{result['usage_ratio']*100:.1f}%")
    print(f"  状态：{result['status']}")
    print(f"  方法：{result.get('method', 'unknown')}")
    print()
    
    # 测试 2: 准确计数（如果 tiktoken 可用）
    if TOKEN_COUNTER_AVAILABLE:
        print("测试 2: 准确计数")
        print("-" * 60)
        monitor_accurate = ContextMonitor(threshold=0.8, model_limit=128000, model="gpt-4")
        
        test_messages = [
            {"role": "user", "content": "你好，请帮我写个 Python 脚本"},
            {"role": "assistant", "content": "好的，请问需要什么功能的脚本？"},
            {"role": "user", "content": "需要一个文件批量重命名的脚本"},
        ] * 20  # 60 条消息
        
        result = monitor_accurate.count_tokens_accurate(test_messages)
        print(f"  消息数：{result['message_count']}")
        print(f"  准确 token: {result['estimated_tokens']:,}")
        print(f"  使用率：{result['usage_ratio']*100:.1f}%")
        print(f"  状态：{result['status']}")
        print(f"  方法：{result.get('method', 'unknown')}")
        print(f"  模型：{result.get('model', 'N/A')}")
        print(f"  Encoding: {result.get('encoding', 'N/A')}")
        print()
        
        # 对比
        print("对比：粗略估算 vs 准确计数")
        print("-" * 60)
        rough = monitor.estimate_from_message_count(60)
        accurate = result
        diff = rough['estimated_tokens'] - accurate['estimated_tokens']
        diff_pct = (diff / accurate['estimated_tokens']) * 100
        print(f"  粗略估算：{rough['estimated_tokens']:,} tokens")
        print(f"  准确计数：{accurate['estimated_tokens']:,} tokens")
        print(f"  差异：{diff:+,} tokens ({diff_pct:+.1f}%)")
        print()
    
    print("=" * 80)


if __name__ == "__main__":
    main()
