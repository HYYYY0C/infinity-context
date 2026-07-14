#!/usr/bin/env python3
"""
单元测试 - Smart Summarizer 模块
"""

import unittest
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from smart_summarizer import SmartSummarizer


class TestSmartSummarizer(unittest.TestCase):
    """SmartSummarizer 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.summarizer = SmartSummarizer(template="default")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.summarizer.max_length, 500)
        self.assertEqual(self.summarizer.min_length, 300)
    
    def test_load_template(self):
        """测试模板加载"""
        # 测试默认模板
        default_template = self.summarizer._load_template("default")
        self.assertIn("{core_tasks}", default_template)
        
        # 测试精简模板
        minimal_template = self.summarizer._load_template("minimal")
        self.assertIn("**核心任务**", minimal_template)
        
        # 测试详细模板
        detailed_template = self.summarizer._load_template("detailed")
        self.assertIn("技术操作详情", detailed_template)
    
    def test_generate_summary(self):
        """测试摘要生成"""
        summary = self.summarizer.generate()
        
        # 检查基本结构
        self.assertIn("## 📝 Session 摘要", summary)
        self.assertIn("### 🎯 核心任务", summary)
        self.assertIn("### 🔧 关键操作", summary)
        self.assertIn("### ⏳ 待办事项", summary)
        
        # 检查长度
        length = len(summary)
        self.assertGreater(length, 200)
        self.assertLess(length, 1000)  # 合理范围
    
    def test_validate_length(self):
        """测试长度验证"""
        # 正常长度
        normal_summary = "A" * 350
        self.assertTrue(self.summarizer.validate_length(normal_summary))
        
        # 太短
        short_summary = "A" * 100
        self.assertFalse(self.summarizer.validate_length(short_summary))
        
        # 较长（在 50% 浮动范围内）
        long_summary = "A" * 700  # 500 * 1.5 = 750，所以 700 应该通过
        self.assertTrue(self.summarizer.validate_length(long_summary))
        
        # 过长（超出 50% 浮动）
        too_long_summary = "A" * 800  # 超出 750 上限
        self.assertFalse(self.summarizer.validate_length(too_long_summary))


if __name__ == "__main__":
    unittest.main()
