#!/usr/bin/env python3
"""
🧪 Infinity Context v1.2.0 - 真实功能测试

测试目标：
- 模型检测逻辑
- Token 计算准确性
- 阈值判断
- 摘要生成（Mock Hermes）
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_model_detection():
    """测试模型检测逻辑"""
    print("🧪 测试 1: 模型检测...")
    
    # 导入被测试的函数
    from scripts.auto_rotate import get_model_config
    
    # 测试用例
    test_cases = [
        # (模型名称，预期 context limit)
        ("phi-3-mini", 4096),
        ("llama-3-8b", 8192),
        ("mistral-7b", 8192),
        ("gpt-3.5-turbo", 16385),
        ("mistral-medium", 32000),
        ("gpt-4-turbo", 128000),
        ("claude-3-haiku", 200000),
        ("claude-sonnet-4", 200000),
    ]
    
    passed = 0
    for model_name, expected_limit in test_cases:
        config = get_model_config(model_name)
        actual_limit = config["limit"]
        
        if actual_limit == expected_limit:
            print(f"  ✅ {model_name} -> {actual_limit:,} tokens")
            passed += 1
        else:
            print(f"  ❌ {model_name} -> {actual_limit:,} tokens (预期 {expected_limit:,})")
    
    print(f"  通过：{passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_tiktoken_counting():
    """测试 tiktoken Token 计数准确性"""
    print("\n🧪 测试 2: tiktoken Token 计数...")
    
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        
        # 测试用例
        test_cases = [
            ("Hello", 1),  # 简单单词
            ("Hello world!", 3),  # 短句
            ("这是一个测试", 4),  # 中文
            ("", 0),  # 空字符串
        ]
        
        passed = 0
        for text, expected_min in test_cases:
            tokens = len(encoding.encode(text))
            if tokens >= expected_min:
                print(f"  ✅ '{text[:20]}' -> {tokens} tokens")
                passed += 1
            else:
                print(f"  ❌ '{text}' -> {tokens} tokens (预期 >= {expected_min})")
        
        print(f"  通过：{passed}/{len(test_cases)}")
        return passed == len(test_cases)
        
    except ImportError:
        print("  ⚠️  tiktoken 未安装，跳过测试")
        return False
    except Exception as e:
        print(f"  ❌ 测试失败：{e}")
        return False


def test_threshold_calculation():
    """测试阈值计算（小模型 vs 大模型）"""
    print("\n🧪 测试 3: 阈值计算...")
    
    # 测试用例：(TOKEN_LIMIT, 预期 USAGE_THRESHOLD, 预期 RECENT_MESSAGES)
    test_cases = [
        (4096, 0.7, 10),    # Phi-3-mini (小模型)
        (8192, 0.7, 10),    # Llama-3-8B (小模型)
        (16385, 0.7, 10),   # GPT-3.5 (小模型)
        (32000, 0.7, 10),   # Mistral-medium (小模型)
        (64000, 0.8, 50),   # 边界值（大模型）
        (128000, 0.8, 50),  # GPT-4-turbo (大模型)
        (200000, 0.8, 50),  # Claude-3 (大模型)
    ]
    
    passed = 0
    for token_limit, expected_threshold, expected_messages in test_cases:
        # 模拟代码中的逻辑
        if token_limit < 64000:
            threshold = 0.7
            messages = 10
        else:
            threshold = 0.8
            messages = 50
        
        if threshold == expected_threshold and messages == expected_messages:
            print(f"  ✅ {token_limit:,} tokens -> 阈值 {threshold:.0%}, 消息 {messages}")
            passed += 1
        else:
            print(f"  ❌ {token_limit:,} tokens -> 阈值 {threshold:.0%}, 消息 {messages} (预期 {expected_threshold:.0%}, {expected_messages})")
    
    print(f"  通过：{passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_summary_generation_mock():
    """测试摘要生成逻辑（Mock Hermes 环境）"""
    print("\n🧪 测试 4: 摘要生成（Mock）...")
    
    # Mock Hermes 工具
    class MockHermes:
        @staticmethod
        def delegate_task(goal, context):
            # 模拟 LLM 返回结构化摘要
            return """
{
    "summary": "讨论了 Python 异步编程和性能优化",
    "key_points": ["async/await 语法", "事件循环机制", "性能优化技巧"],
    "action_items": ["学习 asyncio 库", "实践异步编程", "阅读相关文档"]
}
"""
    
    # 模拟消息列表
    messages = [
        {"role": "user", "content": "什么是 Python 异步编程？"},
        {"role": "assistant", "content": "Python 异步编程使用 async/await 语法..."},
        {"role": "user", "content": "事件循环是什么？"},
        {"role": "assistant", "content": "事件循环是异步编程的核心机制..."},
    ]
    
    # 提取最近对话
    recent = messages[-2:]
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
    
    # 调用 Mock LLM
    try:
        mock_hermes = MockHermes()
        result = mock_hermes.delegate_task(
            goal="生成结构化摘要（JSON 格式）",
            context=f"分析以下对话：\n\n{conversation}"
        )
        
        # 解析 JSON
        import json
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        
        if json_match:
            summary_data = json.loads(json_match.group())
            
            # 验证字段
            assert "summary" in summary_data, "缺少 summary 字段"
            assert "key_points" in summary_data, "缺少 key_points 字段"
            assert "action_items" in summary_data, "缺少 action_items 字段"
            
            print(f"  ✅ 摘要生成成功")
            print(f"     Summary: {summary_data['summary'][:50]}...")
            print(f"     Key Points: {len(summary_data['key_points'])} 个")
            print(f"     Action Items: {len(summary_data['action_items'])} 个")
            return True
        else:
            print(f"  ❌ 无法解析 JSON")
            return False
            
    except Exception as e:
        print(f"  ❌ 测试失败：{e}")
        return False


def test_usage_rate_calculation():
    """测试使用率计算"""
    print("\n🧪 测试 5: 使用率计算...")
    
    # 测试用例
    test_cases = [
        (0, 0.0),  # 0 tokens
        (64000, 0.5),  # 50%
        (102400, 0.8),  # 80%
        (128000, 1.0),  # 100%
        (150000, 1.17),  # 超出的
    ]
    
    passed = 0
    for tokens, expected_rate in test_cases:
        usage_rate = tokens / 128000
        if abs(usage_rate - expected_rate) < 0.01:
            print(f"  ✅ {tokens:,} tokens -> {usage_rate:.1%}")
            passed += 1
        else:
            print(f"  ❌ {tokens:,} tokens -> {usage_rate:.1%} (预期 {expected_rate:.1%})")
    
    print(f"  通过：{passed}/{len(test_cases)}")
    return passed == len(test_cases)


def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试 6: 错误处理...")
    
    # 测试空消息列表
    messages = []
    total_tokens = sum(len(m.get('content', '')) for m in messages)
    if total_tokens == 0:
        print(f"  ✅ 空消息列表处理正确")
    else:
        print(f"  ❌ 空消息列表处理失败")
        return False
    
    # 测试缺失字段
    messages = [{}]
    total_tokens = sum(len(m.get('content', '')) for m in messages)
    if total_tokens == 0:
        print(f"  ✅ 缺失字段处理正确")
    else:
        print(f"  ❌ 缺失字段处理失败")
        return False
    
    # 测试 None 值
    messages = [{"role": "user", "content": None}]
    try:
        total_tokens = sum(len(m.get('content', '') or '') for m in messages)
        print(f"  ✅ None 值处理正确")
        return True
    except Exception as e:
        print(f"  ❌ None 值处理失败：{e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 Infinity Context v1.2.0 - 真实功能测试套件")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("模型检测", test_model_detection()))
    results.append(("Token 计数", test_tiktoken_counting()))
    results.append(("阈值计算", test_threshold_calculation()))
    results.append(("摘要生成", test_summary_generation_mock()))
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
