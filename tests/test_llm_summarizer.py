#!/usr/bin/env python3
"""测试 LLM 摘要生成器"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_summarizer import LLMSummarizer, quick_summarize


def test_llm_summarizer_basic():
    """测试基本功能"""
    print("="*60)
    print("测试 1: 基本摘要生成")
    print("="*60)
    
    conversation = """
    User: 我想创建一个医药供应链 SaaS 平台
    Assistant: 很好的想法！你能说说具体的功能规划吗？
    User: 主要包括：库存管理、订单处理、用药咨询、数据分析
    Assistant: 明白了。技术栈方面有什么考虑？
    User: 后端用 FastAPI，前端用 Vue.js，数据库用 PostgreSQL
    Assistant: 好的。那我们先从库存管理模块开始设计...
    User: 库存管理需要支持多仓库、批次追踪、有效期预警
    Assistant: 收到。我会设计相应的数据模型和 API...
    """
    
    summarizer = LLMSummarizer(model="gpt-3.5-turbo", max_length=400)
    result = summarizer.generate(conversation)
    
    print("\n✅ 摘要生成成功！")
    print(f"\n📌 核心摘要:\n{result.summary_text}")
    print(f"\n🔑 关键点:")
    for point in result.key_points:
        print(f"  - {point}")
    print(f"\n✅ 待办:")
    for item in result.action_items:
        print(f"  - {item}")
    print(f"\n📎 上下文:")
    for key, value in result.context_items.items():
        print(f"  - {key}: {value}")
    print(f"\n🚀 下一步:\n{result.next_steps}")
    print(f"\n📊 置信度：{result.confidence:.0%}")
    print(f"📊 Token 使用：{result.tokens_used}")
    print(f"📊 使用模型：{result.model_used}")


def test_quick_summarize():
    """测试快速摘要函数"""
    print("\n" + "="*60)
    print("测试 2: 快速摘要函数")
    print("="*60)
    
    conversation = """
    User: 帮我优化这段 Python 代码的性能
    Assistant: 当然可以！让我看看...这段代码使用了嵌套循环，时间复杂度是 O(n²)
    User: 那怎么优化？
    Assistant: 可以用哈希表来优化，把时间复杂度降到 O(n)
    User: 具体怎么写？
    Assistant: 使用字典来存储中间结果，避免重复计算...
    User: 明白了！那测试覆盖率呢？
    Assistant: 建议至少达到 80%，重点测试边界情况
    """
    
    markdown = quick_summarize(conversation, max_length=300)
    print("\n" + markdown)


def test_custom_instructions():
    """测试自定义指令"""
    print("\n" + "="*60)
    print("测试 3: 自定义指令")
    print("="*60)
    
    conversation = """
    User: 我在开发一个 B 站视频自动化工具
    Assistant: 听起来很有趣！具体功能是什么？
    User: 从 YouTube 下载视频，自动翻译字幕，然后上传到 B 站
    Assistant: 技术实现呢？
    User: 用 yt-dlp 下载，Whisper 转录，LLM 翻译，biliup 上传
    Assistant: 完整的流程啊！遇到什么问题了吗？
    User: cookies 认证和上传限流的问题
    Assistant: cookies 问题可以通过 MongoDB 共享解决，限流需要等待 24 小时
    """
    
    summarizer = LLMSummarizer(model="gpt-3.5-turbo")
    result = summarizer.generate(
        conversation,
        custom_instructions="重点关注技术栈和解决方案，忽略闲聊内容"
    )
    
    print("\n✅ 带自定义指令的摘要:")
    print(f"\n📌 核心摘要:\n{result.summary_text}")
    print(f"\n🔑 关键点:")
    for point in result.key_points:
        print(f"  - {point}")


def test_error_handling():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试 4: 错误处理")
    print("="*60)
    
    summarizer = LLMSummarizer(model="invalid-model")
    
    try:
        # 这个应该会失败（因为模型不存在）
        result = summarizer.generate("测试对话")
        print("❌ 应该抛出异常但没有")
    except Exception as e:
        print(f"✅ 正确捕获异常：{type(e).__name__}")
        print(f"   消息：{str(e)[:100]}...")


def test_markdown_generation():
    """测试 Markdown 生成"""
    print("\n" + "="*60)
    print("测试 5: Markdown 格式输出")
    print("="*60)
    
    from src.llm_summarizer import SummaryResult
    
    # 手动创建结果
    result = SummaryResult(
        summary_text="本次对话讨论了项目优化方案。",
        key_points=["优化摘要算法", "使用 LLM 替代模板", "支持多后端"],
        action_items=["实现 OpenAI 集成", "添加 Anthropic 支持", "编写文档"],
        context_items={
            "项目": "Infinity Context",
            "版本": "v0.3.0",
            "技术栈": "Python, OpenAI API"
        },
        next_steps="接下来实现 LLM 集成并编写文档。",
        confidence=0.95,
        model_used="gpt-3.5-turbo",
        tokens_used=150
    )
    
    summarizer = LLMSummarizer()
    markdown = summarizer.generate_markdown(result)
    
    print(markdown)


if __name__ == "__main__":
    print("\n🧪 开始测试 LLM 摘要生成器...\n")
    
    # 运行所有测试
    test_llm_summarizer_basic()
    test_quick_summarize()
    test_custom_instructions()
    test_error_handling()
    test_markdown_generation()
    
    print("\n" + "="*60)
    print("✅ 所有测试完成！")
    print("="*60)
    print("\n💡 提示:")
    print("  - 当前使用模拟响应（mock）")
    print("  - 配置 API Key 后可启用真实 LLM 调用")
    print("  - 详见：src/llm_summarizer.py 中的 _call_openai() 等方法")
    print()
