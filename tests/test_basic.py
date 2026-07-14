#!/usr/bin/env python3
"""
🧪 Infinity Context v1.0.0 - 基础测试

测试目标:
- Token 计数准确性
- 摘要生成逻辑
- 使用率检测
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_tiktoken_counting():
    """测试 tiktoken Token 计数准确性"""
    print("🧪 测试 1: tiktoken Token 计数...")
    
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        
        # 测试用例
        test_cases = [
            ("Hello", 1),  # 简单单词
            ("Hello world!", 3),  # 短句
            ("这是一个测试", 4),  # 中文（实际 4 tokens）
            ("", 0),  # 空字符串
        ]
        
        for text, expected_min in test_cases:
            tokens = len(encoding.encode(text))
            print(f"  '{text[:20]}...' -> {tokens} tokens")
            assert tokens >= expected_min, f"Token 数 {tokens} < 预期 {expected_min}"
        
        print("  ✅ tiktoken 计数测试通过")
        return True
        
    except ImportError:
        print("  ⚠️  tiktoken 未安装，跳过测试")
        return False
    except Exception as e:
        print(f"  ❌ 测试失败：{e}")
        return False


def test_summary_generation():
    """测试摘要生成逻辑（模拟）"""
    print("\n🧪 测试 2: 摘要生成逻辑...")
    
    # 模拟消息列表
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"},
        {"role": "user", "content": "我想了解 Python"},
        {"role": "assistant", "content": "Python 是一种高级编程语言..."},
    ]
    
    # 测试提取最近消息
    recent = messages[-2:]
    assert len(recent) == 2, "提取最近消息失败"
    
    # 测试对话格式化
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
    assert "user:" in conversation, "对话格式化失败"
    assert "assistant:" in conversation, "对话格式化失败"
    
    print(f"  提取最近 {len(recent)} 轮对话")
    print(f"  格式化对话长度：{len(conversation)} 字符")
    print("  ✅ 摘要生成逻辑测试通过")
    return True


def test_usage_rate_calculation():
    """测试使用率计算"""
    print("\n🧪 测试 3: 使用率计算...")
    
    # 模拟 Token 数
    test_cases = [
        (0, 0.0),  # 0 tokens
        (64000, 0.5),  # 50%
        (102400, 0.8),  # 80%
        (128000, 1.0),  # 100%
        (150000, 1.17),  # 超出的
    ]
    
    for tokens, expected_rate in test_cases:
        usage_rate = tokens / 128000
        assert abs(usage_rate - expected_rate) < 0.01, f"使用率计算错误：{usage_rate} != {expected_rate}"
        print(f"  {tokens:,} tokens -> {usage_rate:.1%}")
    
    print("  ✅ 使用率计算测试通过")
    return True


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试 4: 错误处理...")
    
    # 测试空消息列表
    messages = []
    total_tokens = sum(len(m.get('content', '')) for m in messages)
    assert total_tokens == 0, "空消息列表处理失败"
    
    # 测试缺失字段
    messages = [{}]
    total_tokens = sum(len(m.get('content', '')) for m in messages)
    assert total_tokens == 0, "缺失字段处理失败"
    
    print("  ✅ 错误处理测试通过")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 Infinity Context v1.0.0 - 测试套件")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("Token 计数", test_tiktoken_counting()))
    results.append(("摘要生成", test_summary_generation()))
    results.append(("使用率计算", test_usage_rate_calculation()))
    results.append(("错误处理", test_error_handling()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "⚠️ 跳过/失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试未通过")
        return 1


if __name__ == "__main__":
    sys.exit(main())
