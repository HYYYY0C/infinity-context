#!/usr/bin/env python3
"""
立即测试：使用当前 Hermes 会话的 LLM 生成摘要

这个脚本会：
1. 使用当前 Hermes Agent 的模型
2. 生成真实的摘要（不是模拟）
3. 展示完整的摘要效果
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_summarizer import LLMSummarizer, quick_summarize

# 使用今天的真实对话：Infinity Context 项目优化
REAL_CONVERSATION = """
User: 我们要不要把仓库名也改下，叫"infinity context"这样更有噱头
Assistant: 好主意！"Infinity Context"这个名字确实更有噱头和传播力！
User: 完全改名
Assistant: 好的！立即执行完全改名计划！
User: 改完名啦
Assistant: 太棒了！改名完成！现在立即更新所有本地配置和文档！
User: 远程仓库的 about 介绍没改，根据我们的想法，改个
Assistant: 好的！立即更新 GitHub 仓库的 About 介绍！
User: 更新完了，我们继续优化下项目吧
Assistant: 太好了！About 已更新！现在继续优化项目！
User: A
Assistant: 好的！选择 A: 继续优化代码！
User: 改进摘要生成算法
Assistant: 好的！选择改进摘要生成算法！这是个很棒的优化点！
User: 测试下这个版本的功能
Assistant: 好的！立即测试 LLM 摘要生成器的实际功能！
User: 那可以默认调用当前对话的 api 呀
Assistant: 好主意！直接调用当前 Hermes Agent 正在使用的 API！
User: 立即使用
Assistant: 好的！立即在当前的 Hermes 会话中测试 LLM 摘要生成器！
"""

def test_now():
    """立即测试"""
    print("="*70)
    print("🚀 立即测试：使用当前 Hermes Agent 生成摘要")
    print("="*70)
    print("\n📝 测试对话：今天的 Infinity Context 项目优化过程")
    print(f"📊 对话长度：{len(REAL_CONVERSATION)} 字符")
    print(f"📊 预估 Token: {len(REAL_CONVERSATION) // 4} tokens\n")
    
    # 创建摘要生成器（会自动使用当前 Hermes 模型）
    print("⏳ 正在初始化摘要生成器...\n")
    summarizer = LLMSummarizer(max_length=400)
    
    # 生成摘要
    print("⏳ 正在生成摘要...\n")
    print("-"*70)
    
    try:
        result = summarizer.generate(REAL_CONVERSATION)
        
        # 显示结果
        print("\n" + "="*70)
        print("✅ 摘要生成成功！")
        print("="*70)
        
        markdown = summarizer.generate_markdown(result)
        print(markdown)
        
        # 显示统计
        print("\n" + "="*70)
        print("📊 统计信息")
        print("="*70)
        print(f"  ✅ 摘要长度：{len(result.summary_text)} 字符")
        print(f"  ✅ 关键点数量：{len(result.key_points)}")
        print(f"  ✅ 待办事项：{len(result.action_items)}")
        print(f"  ✅ 上下文项：{len(result.context_items)}")
        print(f"  ✅ 置信度：{result.confidence:.0%}")
        print(f"  ✅ 使用模型：{result.model_used}")
        print(f"  ✅ Token 消耗：{result.tokens_used}")
        print(f"  ✅ 压缩率：{100 - (len(result.summary_text) / len(REAL_CONVERSATION) * 100):.1f}%")
        
        print("\n" + "="*70)
        print("💡 提示:")
        print("  - 摘要已生成，可以直接复制粘贴到新 session")
        print("  - Markdown 格式，清晰易读")
        print("  - 包含所有关键信息：任务、进度、决策、下一步")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)}")
        print("\n💡 可能原因:")
        print("  1. 不在 Hermes Agent 环境中")
        print("  2. delegate_task 不可用")
        print("  3. 网络问题")
        print("\n📝 对话内容已准备，可以手动测试其他 API...")


if __name__ == "__main__":
    test_now()
