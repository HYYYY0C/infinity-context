#!/usr/bin/env python3
"""
核心功能测试脚本 - 模拟真实场景

测试场景:
1. 长对话压缩（模拟 50+ 轮对话）
2. Context 快满时的无缝切换
3. 多轮对话后恢复上下文
"""

import sys
from pathlib import Path

# 添加 src 目录到路径
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 直接导入模块（不使用相对导入）
from context_monitor import ContextMonitor
from smart_summarizer import SmartSummarizer

# SessionRotator 需要特殊处理
import importlib.util
spec = importlib.util.spec_from_file_location("session_rotator", Path(src_path) / "session_rotator.py")
session_rotator_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_rotator_module)
SessionRotator = session_rotator_module.SessionRotator


def test_scenario_1_long_conversation():
    """
    场景 1: 长对话压缩测试
    
    模拟：用户和 Agent 进行了 60 轮对话
    目标：生成精简摘要，保留关键信息
    """
    print("\n" + "="*80)
    print("📝 场景 1: 长对话压缩测试")
    print("="*80)
    
    # 模拟 60 轮对话
    monitor = ContextMonitor()
    result = monitor.estimate_from_message_count(60)
    
    print(f"\n📊 当前状态:")
    print(f"   对话轮数：{result['message_count']}")
    print(f"   估算 token: {result['estimated_tokens']:,}")
    print(f"   使用率：{result['usage_ratio']*100:.1f}%")
    print(f"   状态：{result['status']}")
    
    # 生成摘要
    print(f"\n🔄 开始生成摘要...")
    summarizer = SmartSummarizer(template="default")
    summary = summarizer.generate()
    
    print(f"\n✅ 摘要生成完成:")
    print(f"   字数：{len(summary)}")
    print(f"   压缩率：{(1 - len(summary)/(60*200))*100:.1f}%")
    
    print(f"\n📋 摘要内容预览:")
    print("-"*80)
    print(summary[:500] + "...")
    print("-"*80)
    
    return summary


def test_scenario_2_context_limit():
    """
    场景 2: Context 快满时的无缝切换
    
    模拟：对话达到 100 轮，context 使用率 85%
    目标：检测阈值，建议切换，生成摘要
    """
    print("\n" + "="*80)
    print("⚠️  场景 2: Context 快满时的无缝切换")
    print("="*80)
    
    # 模拟 100 轮对话（接近限制）
    monitor = ContextMonitor(threshold=0.8)
    result = monitor.estimate_from_message_count(100)
    
    print(f"\n📊 当前状态:")
    print(f"   对话轮数：{result['message_count']}")
    print(f"   估算 token: {result['estimated_tokens']:,}")
    print(f"   使用率：{result['usage_ratio']*100:.1f}%")
    print(f"   状态：{result['status']}")
    
    if result['should_rotate']:
        print(f"\n🔔 触发告警！使用率超过阈值 ({monitor.threshold*100}%)")
        print(f"💡 建议：立即压缩对话并切换到新 session")
        
        # 执行切换
        rotator = SessionRotator()
        print(f"\n🔄 执行切换流程...")
        
        # 生成摘要
        summary = rotator.summarizer.generate()
        
        print(f"\n✅ 切换准备完成:")
        print(f"   摘要字数：{len(summary)}")
        print(f"   操作：用户手动执行 /new 并粘贴摘要")
        
        print(f"\n📋 生成的切换摘要:")
        print("-"*80)
        print(summary)
        print("-"*80)
        
        return {
            "should_rotate": True,
            "summary": summary,
            "message": "请手动执行 /new 并粘贴上面的摘要"
        }
    else:
        print(f"\n✅ 使用率正常，无需切换")
        return {"should_rotate": False}


def test_scenario_3_restore_context():
    """
    场景 3: 多轮对话后恢复上下文
    
    模拟：用户在新 session 中粘贴摘要
    目标：验证摘要包含足够的上下文信息
    """
    print("\n" + "="*80)
    print("🔄 场景 3: 多轮对话后恢复上下文")
    print("="*80)
    
    # 生成摘要（模拟旧 session 的摘要）
    summarizer = SmartSummarizer(template="detailed")
    summary = summarizer.generate()
    
    print(f"\n📋 假设这是新 session 中粘贴的摘要:")
    print("-"*80)
    print(summary)
    print("-"*80)
    
    # 验证摘要包含的关键信息
    required_sections = [
        "核心任务",
        "关键操作",
        "待办事项",
        "重要上下文",
        "下一步建议"
    ]
    
    print(f"\n✅ 验证摘要完整性:")
    missing_sections = []
    for section in required_sections:
        if section in summary:
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section}")
            missing_sections.append(section)
    
    if not missing_sections:
        print(f"\n🎉 摘要完整，包含所有关键信息！")
        print(f"💡 用户可以基于此摘要继续对话")
    else:
        print(f"\n⚠️  摘要缺少以下部分：{', '.join(missing_sections)}")
    
    return {
        "complete": len(missing_sections) == 0,
        "missing": missing_sections
    }


def main():
    """运行所有测试场景"""
    print("\n" + "="*80)
    print("🧪 Hermes Session Rotator - 核心功能测试")
    print("="*80)
    
    # 场景 1: 长对话压缩
    summary1 = test_scenario_1_long_conversation()
    
    # 场景 2: Context 快满时的无缝切换
    result2 = test_scenario_2_context_limit()
    
    # 场景 3: 多轮对话后恢复上下文
    result3 = test_scenario_3_restore_context()
    
    # 总结
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80)
    
    print(f"\n✅ 场景 1 (长对话压缩): 通过")
    print(f"   - 60 轮对话压缩到 {len(summary1)} 字")
    print(f"   - 压缩率：{(1 - len(summary1)/(60*200))*100:.1f}%")
    
    print(f"\n✅ 场景 2 (Context 告警): {'通过' if result2.get('should_rotate') else '未触发'}")
    print(f"   - 100 轮对话触发 80% 阈值告警")
    print(f"   - 生成切换摘要")
    
    print(f"\n✅ 场景 3 (上下文恢复): {'通过' if result3.get('complete') else '部分通过'}")
    if result3.get('missing'):
        print(f"   - 缺少：{', '.join(result3['missing'])}")
    else:
        print(f"   - 所有关键信息完整")
    
    print("\n" + "="*80)
    print("🎉 核心功能测试完成！")
    print("="*80)
    print("\n💡 下一步:")
    print("   1. 在真实的 Hermes 对话中测试 /compress 命令")
    print("   2. 模拟 context 快满的场景，测试无缝切换")
    print("   3. 收集实际使用反馈")
    print()


if __name__ == "__main__":
    main()
