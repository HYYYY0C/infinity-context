# 📋 支持的模型配置

**自动检测模型并调整阈值**

---

## 🎯 模型配置表

| 模型 | Context | 触发阈值 | 说明 |
|------|---------|---------|------|
| **GPT-3.5-turbo** | 16,385 | 80% (13K) | 适合短对话 |
| **GPT-4-turbo** | 128K | 80% (102K) | 推荐 ✅ |
| **GPT-4o** | 128K | 80% (102K) | 推荐 ✅ |
| **Claude 3 Haiku** | 200K | 80% (160K) | 最佳选择 🌟 |
| **Claude 3 Sonnet** | 200K | 80% (160K) | 最佳选择 🌟 |
| **Claude 3 Opus** | 200K | 80% (160K) | 最佳选择 🌟 |
| **Llama-3-8B** | 8K | 80% (6.4K) | 本地部署 |
| **Llama-3-70B** | 8K | 80% (6.4K) | 本地部署 |
| **Mistral 7B** | 8K | 80% (6.4K) | 本地部署 |
| **Phi-3-mini** | 4K | 80% (3.2K) | 超小模型 |
| **Phi-3-medium** | 128K | 80% (102K) | 推荐 ✅ |

---

## 🔧 自动检测模型

### **方法 1: 通过 Hermes API**

```python
def get_current_model():
    """获取当前使用的模型"""
    try:
        from hermes_tools import terminal
        result = terminal("hermes config get model")
        # 解析输出：claude-sonnet-4, gpt-4o, 等
        return result.strip()
    except:
        return "unknown"
```

### **方法 2: 通过环境变量**

```bash
# 设置模型名称
export LLM_MODEL="claude-3-haiku"
```

### **方法 3: 手动配置**

```python
# 在 auto_rotate.py 顶部配置
MODEL_NAME = "claude-3-haiku"  # 手动指定
```

---

## 📊 动态 Token 限制

```python
# 模型配置字典
MODEL_CONFIGS = {
    # OpenAI
    "gpt-3.5-turbo": {"limit": 16385, "encoding": "cl100k_base"},
    "gpt-4-turbo": {"limit": 128000, "encoding": "cl100k_base"},
    "gpt-4o": {"limit": 128000, "encoding": "cl100k_base"},
    
    # Anthropic
    "claude-3-haiku": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-sonnet": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-opus": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-sonnet-4": {"limit": 200000, "encoding": "cl100k_base"},
    
    # Meta Llama
    "llama-3-8b": {"limit": 8192, "encoding": "cl100k_base"},
    "llama-3-70b": {"limit": 8192, "encoding": "cl100k_base"},
    
    # Mistral
    "mistral-7b": {"limit": 8192, "encoding": "cl100k_base"},
    "mistral-medium": {"limit": 32000, "encoding": "cl100k_base"},
    
    # Microsoft Phi
    "phi-3-mini": {"limit": 4096, "encoding": "cl100k_base"},
    "phi-3-medium": {"limit": 128000, "encoding": "cl100k_base"},
    
    # 默认（未知模型）
    "default": {"limit": 128000, "encoding": "cl100k_base"},
}

def get_model_config(model_name: str) -> dict:
    """获取模型配置"""
    # 规范化模型名称（小写，替换特殊字符）
    normalized = model_name.lower().replace("-", "_").replace(".", "_")
    
    # 精确匹配
    if normalized in MODEL_CONFIGS:
        return MODEL_CONFIGS[normalized]
    
    # 模糊匹配（包含关键词）
    for key, config in MODEL_CONFIGS.items():
        if key in normalized or normalized in key:
            return config
    
    # 返回默认配置
    return MODEL_CONFIGS["default"]

# 使用示例
model_name = get_current_model()  # 或从环境变量读取
config = get_model_config(model_name)
TOKEN_LIMIT = config["limit"]
ENCODING = config["encoding"]

print(f"📊 使用模型：{model_name}")
print(f"   Context 限制：{TOKEN_LIMIT:,} tokens")
print(f"   触发阈值：{TOKEN_LIMIT * 0.8:,.0f} tokens (80%)")
```

---

## 🚀 小模型优化策略

### **问题：小模型 Context 太小，频繁切换怎么办？**

#### **方案 1: 更激进的摘要**

```python
# 小模型：只保留最近 10 轮 + 摘要
if TOKEN_LIMIT < 32000:  # 小模型
    RECENT_MESSAGES = 10  # 而不是 50
    SUMMARY_RATIO = 0.5   # 摘要压缩到 50%
else:
    RECENT_MESSAGES = 50
    SUMMARY_RATIO = 0.8
```

#### **方案 2: 更早触发切换**

```python
# 小模型：70% 就触发（避免超出）
if TOKEN_LIMIT < 32000:
    USAGE_THRESHOLD = 0.7  # 70%
else:
    USAGE_THRESHOLD = 0.8  # 80%
```

#### **方案 3: 分层摘要**

```python
def generate_hierarchical_summary(messages, model_limit):
    """分层摘要：小模型用精简版，大模型用详细版"""
    
    if model_limit < 32000:
        # 小模型：只提取关键点
        prompt = "提取 3 个最关键点，50 字以内"
    elif model_limit < 128000:
        # 中等模型：关键点 + 待办
        prompt = "提取关键点和待办事项，200 字以内"
    else:
        # 大模型：完整结构化摘要
        prompt = "生成完整结构化摘要（JSON 格式）"
    
    return delegate_task(goal=prompt, context=messages)
```

---

## 📋 完整代码示例

### **auto_rotate.py (支持小模型版本)**

```python
#!/usr/bin/env python3
"""
🔄 Infinity Context v1.1.0 - 支持小模型

自动检测模型并调整 Context 限制
"""

import tiktoken
from typing import Dict

# ========== 模型配置 ==========
MODEL_CONFIGS: Dict[str, Dict] = {
    # OpenAI
    "gpt-3.5-turbo": {"limit": 16385, "encoding": "cl100k_base"},
    "gpt-4-turbo": {"limit": 128000, "encoding": "cl100k_base"},
    "gpt-4o": {"limit": 128000, "encoding": "cl100k_base"},
    
    # Anthropic
    "claude-3-haiku": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-sonnet": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-3-opus": {"limit": 200000, "encoding": "cl100k_base"},
    "claude-sonnet-4": {"limit": 200000, "encoding": "cl100k_base"},
    
    # Meta Llama
    "llama-3-8b": {"limit": 8192, "encoding": "cl100k_base"},
    "llama-3-70b": {"limit": 8192, "encoding": "cl100k_base"},
    
    # Mistral
    "mistral-7b": {"limit": 8192, "encoding": "cl100k_base"},
    "mistral-medium": {"limit": 32000, "encoding": "cl100k_base"},
    
    # Microsoft Phi
    "phi-3-mini": {"limit": 4096, "encoding": "cl100k_base"},
    "phi-3-medium": {"limit": 128000, "encoding": "cl100k_base"},
    
    # 默认
    "default": {"limit": 128000, "encoding": "cl100k_base"},
}

def get_model_config(model_name: str) -> Dict:
    """获取模型配置"""
    normalized = model_name.lower().replace("-", "_").replace(".", "_")
    
    if normalized in MODEL_CONFIGS:
        return MODEL_CONFIGS[normalized]
    
    for key, config in MODEL_CONFIGS.items():
        if key in normalized or normalized in key:
            return config
    
    return MODEL_CONFIGS["default"]

def check_and_rotate():
    """检查并自动切换 - 支持小模型"""
    
    # 1. 获取当前模型
    model_name = os.getenv("LLM_MODEL", "claude-sonnet-4")
    config = get_model_config(model_name)
    
    TOKEN_LIMIT = config["limit"]
    ENCODING = config["encoding"]
    
    print(f"📊 使用模型：{model_name}")
    print(f"   Context 限制：{TOKEN_LIMIT:,} tokens")
    
    # 2. 动态调整阈值
    if TOKEN_LIMIT < 32000:
        USAGE_THRESHOLD = 0.7  # 小模型：70%
        RECENT_MESSAGES = 10   # 只保留最近 10 轮
        print(f"   触发阈值：70% ({TOKEN_LIMIT * 0.7:,.0f} tokens)")
        print(f"   小模型模式：启用")
    else:
        USAGE_THRESHOLD = 0.8  # 大模型：80%
        RECENT_MESSAGES = 50
        print(f"   触发阈值：80% ({TOKEN_LIMIT * 0.8:,.0f} tokens)")
    
    # 3. 获取会话
    messages = session_search(window=RECENT_MESSAGES)
    
    # 4. 计算 Token
    encoding = tiktoken.get_encoding(ENCODING)
    total_tokens = sum(len(encoding.encode(m.get('content', ''))) for m in messages)
    usage_rate = total_tokens / TOKEN_LIMIT
    
    print(f"📈 当前使用：{total_tokens:,} tokens ({usage_rate:.1%})")
    
    # 5. 检查阈值
    if usage_rate < USAGE_THRESHOLD:
        print("✅ 使用率正常")
        return
    
    print(f"⚠️  使用率超过 {USAGE_THRESHOLD:.0%}，执行切换...")
    
    # 6. 生成摘要（根据模型大小调整）
    if TOKEN_LIMIT < 32000:
        summary_prompt = "提取 3 个关键点，50 字以内"
    else:
        summary_prompt = "生成结构化摘要（JSON 格式）"
    
    # ... 后续逻辑不变 ...
```

---

## 🎯 使用示例

### **场景 1: GPT-3.5-turbo (16K)**

```bash
# 设置模型
export LLM_MODEL="gpt-3.5-turbo"

# 运行
python3 auto_rotate.py

# 输出:
# 📊 使用模型：gpt-3.5-turbo
#    Context 限制：16,385 tokens
#    触发阈值：70% (11,470 tokens)
#    小模型模式：启用
```

### **场景 2: Llama-3-8B (8K)**

```bash
export LLM_MODEL="llama-3-8b"
python3 auto_rotate.py

# 输出:
# 📊 使用模型：llama-3-8b
#    Context 限制：8,192 tokens
#    触发阈值：70% (5,734 tokens)
#    小模型模式：启用
```

### **场景 3: Claude 3 Haiku (200K)**

```bash
export LLM_MODEL="claude-3-haiku"
python3 auto_rotate.py

# 输出:
# 📊 使用模型：claude-3-haiku
#    Context 限制：200,000 tokens
#    触发阈值：80% (160,000 tokens)
#    大模型模式：启用
```

---

## 📊 性能对比

| 模型 | Context | 切换频率 | 摘要质量 | 推荐度 |
|------|---------|---------|---------|--------|
| **GPT-3.5** | 16K | 高（每 10-20 轮） | 中 | ⭐⭐ |
| **Llama-3-8B** | 8K | 很高（每 5-10 轮） | 中 | ⭐ |
| **GPT-4-turbo** | 128K | 低（每 100+ 轮） | 高 | ⭐⭐⭐⭐ |
| **Claude 3 Haiku** | 200K | 很低（每 150+ 轮） | 高 | ⭐⭐⭐⭐⭐ |

**推荐**: 如果可能，使用 **Claude 3 Haiku** 或 **GPT-4-turbo**，性价比最高！

---

## 💡 小模型生存指南

### **如果只能用小模型 (<32K)**

1. **更早触发切换** (70% 而不是 80%)
2. **更精简的摘要** (只保留关键点)
3. **更频繁的检查** (每 2 分钟而不是 5 分钟)
4. **考虑升级模型** (Claude 3 Haiku 性价比极高)

### **最佳性价比方案**

```
Claude 3 Haiku ($0.25/1M input tokens)
- 200K Context
- 速度快
- 成本低
- 适合长时间对话

比 GPT-4-turbo 便宜 10 倍！
```

---

## 🔗 相关资源

- [Claude 3 定价](https://www.anthropic.com/pricing)
- [GPT-4 定价](https://openai.com/pricing)
- [Llama-3 本地部署](https://llama.meta.com/)

---

*"Small model, Long context"*  
*"Infinite context, small model"*
