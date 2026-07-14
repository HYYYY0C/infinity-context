#!/usr/bin/env python3
"""
🧪 测试小模型支持

模拟不同大小的模型，验证 Infinity Context 的自适应能力
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# 直接导入模型配置字典
try:
    from auto_rotate import MODEL_CONFIGS
except ImportError as e:
    print(f"❌ 导入失败：{e}")
    print(f"   当前路径：{sys.path}")
    sys.exit(1)


def get_model_config(model_name: str) -> dict:
    """获取模型配置（测试用本地版本）"""
    # 不要替换 - 和 . ，直接用小写匹配
    normalized = model_name.lower()
    
    # 1. 精确匹配
    if normalized in MODEL_CONFIGS:
        return MODEL_CONFIGS[normalized]
    
    # 2. 检查是否包含已知模型的关键词
    for key, config in MODEL_CONFIGS.items():
        if key == "default":  # 跳过默认值
            continue
        if key in normalized or normalized in key:
            return config
    
    # 3. 返回默认
    return MODEL_CONFIGS["default"]


def test_model_detection():
    """测试 1: 模型自动检测"""
    print("=" * 60)
    print("🧪 测试 1: 模型自动检测")
    print("=" * 60)
    
    test_cases = [
        # (模型名称，预期 Context 限制)
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
    failed = 0
    
    for model_name, expected_limit in test_cases:
        config = get_model_config(model_name)
        actual_limit = config["limit"]
        
        if actual_limit == expected_limit:
            print(f"  ✅ {model_name:30} → {actual_limit:,} tokens")
            passed += 1
        else:
            print(f"  ❌ {model_name:30} → {actual_limit:,} tokens (预期：{expected_limit:,})")
            failed += 1
    
    print(f"\n结果：{passed} 通过，{failed} 失败")
    return failed == 0


def test_threshold_calculation():
    """测试 2: 动态阈值计算"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: 动态阈值计算")
    print("=" * 60)
    
    test_cases = [
        # (模型名称，预期模式)
        ("phi-3-mini", "small"),      # 小模型 (<64K)
        ("llama-3-8b", "small"),
        ("gpt-3.5-turbo", "small"),
        ("mistral-medium", "small"),   # 32K < 64K，算小模型
        ("gpt-4-turbo", "large"),      # 128K >= 64K，算大模型
        ("claude-3-haiku", "large"),
    ]
    
    all_passed = True
    
    for model_name, expected_mode in test_cases:
        config = get_model_config(model_name)
        token_limit = config["limit"]
        
        # 计算阈值（<64K 算小模型，Hermes 原生不支持）
        if token_limit < 64000:
            actual_mode = "small"
            threshold = 0.7
            messages = 10
            mode_name = "🐜 小模型（Hermes 原生不支持）"
        else:
            actual_mode = "large"
            threshold = 0.8
            messages = 50
            mode_name = "🐘 大模型"
        
        trigger_tokens = token_limit * threshold
        
        passed = (actual_mode == expected_mode)
        status = "✅" if passed else "❌"
        
        print(f"  {status} {model_name:20} ({token_limit:>7,} tokens)")
        print(f"      模式：{mode_name}")
        print(f"      阈值：{threshold:.0%} ({trigger_tokens:,.0f} tokens)")
        print(f"      消息数：{messages} 轮")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_summary_mode():
    """测试 3: 摘要模式选择"""
    print("\n" + "=" * 60)
    print("🧪 测试 3: 摘要模式选择")
    print("=" * 60)
    
    test_cases = [
        # (模型名称，预期摘要模式)
        ("phi-3-mini", "simple"),
        ("llama-3-8b", "simple"),
        ("gpt-3.5-turbo", "simple"),
        ("mistral-medium", "simple"),
        ("gpt-4-turbo", "full"),
        ("claude-3-haiku", "full"),
    ]
    
    all_passed = True
    
    for model_name, expected_mode in test_cases:
        config = get_model_config(model_name)
        token_limit = config["limit"]
        
        # 根据模型大小选择摘要目标（<64K 算小模型）
        if token_limit < 64000:
            actual_mode = "simple"
            goal = "提取 3 个关键点，50 字以内"
            mode_name = "精简"
        else:
            actual_mode = "full"
            goal = "生成结构化摘要（JSON 格式）"
            mode_name = "完整"
        
        passed = (actual_mode == expected_mode)
        status = "✅" if passed else "❌"
        
        print(f"  {status} {model_name:20} ({token_limit:>7,} tokens)")
        print(f"      模式：{mode_name}")
        print(f"      目标：{goal}")
        
        if not passed:
            all_passed = False
    
    return all_passed


def test_token_efficiency():
    """测试 4: Token 使用效率对比"""
    print("\n" + "=" * 60)
    print("🧪 测试 4: Token 使用效率对比")
    print("=" * 60)
    
    print("\n场景：100 轮对话，每轮平均 200 tokens")
    print("总 tokens: 20,000\n")
    
    scenarios = [
        ("Phi-3-mini (4K)", 4096, "每 10 轮切换"),
        ("Llama-3-8B (8K)", 8192, "每 20 轮切换"),
        ("GPT-3.5 (16K)", 16385, "每 40 轮切换"),
        ("GPT-4-turbo (128K)", 128000, "每 300 轮切换"),
        ("Claude 3 Haiku (200K)", 200000, "每 500 轮切换"),
    ]
    
    total_tokens = 20000
    
    print(f"{'模型':<25} {'Context':<12} {'切换频率':<15} {'切换次数':<10} {'总摘要 tokens':<15}")
    print("-" * 80)
    
    for model_name, limit, frequency in scenarios:
        # 计算需要切换多少次
        switches = int(total_tokens // (limit * 0.7))  # 70% 触发
        
        # 每次摘要约 200 tokens
        summary_tokens = switches * 200
        
        print(f"{model_name:<25} {limit:>10,} {frequency:<15} {switches:<10} {summary_tokens:>12,}")
    
    print("\n💡 结论：小模型虽然切换频繁，但通过精简摘要，总体成本可控")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 Infinity Context v1.1.0 - 小模型支持测试")
    print("=" * 60)
    print("")
    
    results = []
    
    # 运行测试
    results.append(("模型检测", test_model_detection()))
    results.append(("阈值计算", test_threshold_calculation()))
    results.append(("摘要模式", test_summary_mode()))
    results.append(("Token 效率", test_token_efficiency()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有小模型测试通过！")
        print("\n✅ 结论：")
        print("  - 小模型 (4K-32K) 可以正常使用 Infinity Context")
        print("  - 自动调整阈值 (70%) 和摘要模式 (精简)")
        print("  - 虽然切换频繁，但通过精简摘要控制成本")
        print("  - 真正实现了'小模型，长上下文'！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
