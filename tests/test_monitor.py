#!/usr/bin/env python3
"""
单元测试 - Context Monitor 模块
"""

import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from context_monitor import ContextMonitor


class TestContextMonitor(unittest.TestCase):
    """ContextMonitor 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.monitor = ContextMonitor(threshold=0.8, model_limit=128000)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.monitor.threshold, 0.8)
        self.assertEqual(self.monitor.model_limit, 128000)
        self.assertEqual(self.monitor.avg_tokens_per_message, 200)
    
    def test_estimate_from_message_count(self):
        """测试消息数量估算"""
        result = self.monitor.estimate_from_message_count(50)
        
        self.assertEqual(result["message_count"], 50)
        self.assertEqual(result["estimated_tokens"], 10000)  # 50 * 200
        self.assertAlmostEqual(result["usage_ratio"], 0.078, places=2)
        self.assertFalse(result["should_rotate"])
    
    def test_should_rotate_high_usage(self):
        """测试高使用率时建议旋转"""
        result = self.monitor.estimate_from_message_count(600)
        
        self.assertTrue(result["should_rotate"])
        self.assertGreater(result["usage_ratio"], 0.8)
    
    def test_detect_truncation(self):
        """测试截断检测"""
        self.assertTrue(self.monitor.detect_truncation("...[truncated]"))
        self.assertTrue(self.monitor.detect_truncation("...[内容已截断]"))
        self.assertFalse(self.monitor.detect_truncation("正常内容"))
    
    def test_get_status(self):
        """测试状态获取"""
        # 私有方法测试
        self.assertEqual(
            self.monitor._get_status(0.96), 
            "🔴 紧急（超过 95%）"
        )
        self.assertEqual(
            self.monitor._get_status(0.85), 
            "🟠 警告（建议压缩）"
        )
        self.assertEqual(
            self.monitor._get_status(0.6), 
            "🟡 正常"
        )
        self.assertEqual(
            self.monitor._get_status(0.3), 
            "🟢 健康"
        )


if __name__ == "__main__":
    unittest.main()
