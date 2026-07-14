# 🤖 LLM 摘要生成器使用指南

**Infinity Context** 的 LLM 摘要生成器现在支持**零配置**使用！

---

## 🎯 核心特性

### **自动检测 API（优先级从高到低）**

1. **🥇 Hermes Agent 原生 API** (推荐)
   - ✅ 零配置
   - ✅ 使用当前会话的模型
   - ✅ 自动继承 Hermes 设置
   - ✅ 最智能的选择

2. **🥈 OpenAI API**
   - 需要 `OPENAI_API_KEY` 环境变量
   - 支持 GPT-3.5/4 等模型

3. **🥉 Anthropic API**
   - 需要 `ANTHROPIC_API_KEY` 环境变量
   - 支持 Claude 系列模型

4. **🏅 本地 Ollama**
   - 需要本地运行 Ollama 服务
   - 完全离线，免费

5. **📦 模拟响应** (测试用)
   - 无需任何配置
   - 用于开发和测试

---

## 🚀 快速开始

### **方式 1: 在 Hermes Agent 中使用（推荐）**

**无需任何配置！** 直接在 Hermes 会话中运行：

```python
from src.llm_summarizer import LLMSummarizer

# 创建摘要生成器
summarizer = LLMSummarizer()

# 生成摘要（自动使用当前 Hermes 模型）
result = summarizer.generate(conversation_text)

# 输出 Markdown 格式
print(summarizer.generate_markdown(result))
```

**原理**:
- 自动检测 `hermes_tools` 可用
- 通过 `delegate_task` 调用当前 LLM
- 使用会话中的实际模型（如 astron-code-latest）
- 零配置，开箱即用！

---

### **方式 2: 使用 OpenAI API**

```bash
# 设置环境变量
export OPENAI_API_KEY="sk-..."
```

```python
from src.llm_summarizer import LLMSummarizer

# 指定模型
summarizer = LLMSummarizer(model="gpt-4")

# 生成摘要
result = summarizer.generate(conversation_text)
```

---

### **方式 3: 使用 Anthropic API**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

```python
summarizer = LLMSummarizer(model="claude-3-5-sonnet")
result = summarizer.generate(conversation_text)
```

---

### **方式 4: 使用本地 Ollama**

```bash
# 启动 Ollama
ollama serve

# 拉取模型
ollama pull llama2
```

```python
summarizer = LLMSummarizer(model="llama2")
result = summarizer.generate(conversation_text)
```

---

### **方式 5: 测试模式**

无需任何配置，自动使用模拟响应：

```python
summarizer = LLMSummarizer()
result = summarizer.generate(conversation_text)
# 输出模拟摘要（用于测试）
```

---

## 📊 实际使用示例

### **场景 1: 长对话摘要**

```python
from src.llm_summarizer import LLMSummarizer

# 模拟长对话
conversation = """
User: 我想做一个 YouTube 到 B 站的全自动化工具
Assistant: 很好的想法！具体需要什么功能？
User: 从 YouTube 下载视频，自动转录英文字幕，翻译成中文，生成配音，最后上传到 B 站
...（更多对话）
"""

# 创建摘要生成器
summarizer = LLMSummarizer()

# 生成摘要
result = summarizer.generate(conversation)

# 查看结果
print(f"摘要：{result.summary_text}")
print(f"关键点：{result.key_points}")
print(f"待办：{result.action_items}")
print(f"置信度：{result.confidence:.0%}")

# 输出 Markdown（可直接粘贴到新 session）
markdown = summarizer.generate_markdown(result)
print(markdown)
```

---

### **场景 2: 自定义指令**

```python
result = summarizer.generate(
    conversation,
    custom_instructions="重点关注技术决策和代码变更，忽略闲聊"
)
```

---

### **场景 3: 快速摘要**

```python
from src.llm_summarizer import quick_summarize

markdown = quick_summarize(conversation, max_length=300)
print(markdown)
```

---

## 🔧 高级配置

### **调整参数**

```python
summarizer = LLMSummarizer(
    model="gpt-4",        # 模型名称
    max_length=500,       # 最大摘要长度（字符）
    temperature=0.3       # 温度参数（0.0-1.0）
)
```

### **自定义模板**

虽然 LLM 会自动生成结构化摘要，但你也可以通过 `custom_instructions` 调整输出格式：

```python
result = summarizer.generate(
    conversation,
    custom_instructions="""
请特别关注以下内容：
1. 技术栈和工具选择
2. 架构决策和原因
3. 遇到的问题和解决方案
4. 下一步行动计划
"""
)
```

---

## 🧪 测试

### **运行测试套件**

```bash
# 真实场景测试
python tests/test_real_scenario.py

# Hermes 原生测试（需要在 Hermes 环境中）
python tests/test_hermes_native.py

# 基本功能测试
python tests/test_llm_summarizer.py
```

---

## 📈 性能对比

| 方式 | 配置难度 | 成本 | 速度 | 质量 | 推荐场景 |
|------|---------|------|------|------|---------|
| **Hermes 原生** | ⭐ 零配置 | 💰 现有会话 | ⚡ 快 | 🌟 优秀 | **日常使用** |
| OpenAI | ⭐⭐ API Key | 💰💰 按量付费 | ⚡⚡ 中等 | 🌟🌟 优秀 | 高质量需求 |
| Anthropic | ⭐⭐ API Key | 💰💰 按量付费 | ⚡⚡ 中等 | 🌟🌟🌟 最佳 | 复杂对话 |
| Ollama | ⭐⭐⭐ 本地部署 | 🆓 免费 | ⚡ 快 | 🌟 良好 | 离线/隐私 |
| 模拟 | ⭐ 零配置 | 🆓 免费 | ⚡⚡⚡ 最快 | 📦 测试 | 开发测试 |

---

## 💡 最佳实践

### **1. 在 Hermes 中使用**
```python
# ✅ 推荐：零配置，自动使用当前模型
summarizer = LLMSummarizer()
```

### **2. 控制摘要长度**
```python
# 短摘要（200 字）
summarizer = LLMSummarizer(max_length=200)

# 长摘要（800 字）
summarizer = LLMSummarizer(max_length=800)
```

### **3. 提高准确性**
```python
# 使用更强大的模型（如果可用）
summarizer = LLMSummarizer(model="gpt-4")

# 降低温度，提高确定性
summarizer = LLMSummarizer(temperature=0.1)
```

### **4. 自定义关注点**
```python
# 关注技术细节
result = summarizer.generate(
    conversation,
    custom_instructions="重点关注技术实现细节"
)

# 关注业务逻辑
result = summarizer.generate(
    conversation,
    custom_instructions="重点关注业务流程和需求"
)
```

---

## ❓ 常见问题

### **Q: 如何在 Hermes 外使用？**

A: 配置 API Key 即可：
```bash
export OPENAI_API_KEY="sk-..."
python your_script.py
```

### **Q: 支持哪些模型？**

A: 理论上支持所有 LLM：
- ✅ GPT-3.5/4 (OpenAI)
- ✅ Claude (Anthropic)
- ✅ Llama/Mistral (Ollama)
- ✅ Hermes 使用的任何模型

### **Q: 摘要质量如何？**

A: 取决于使用的模型：
- **Hermes 原生**: 优秀（使用会话中的模型）
- **GPT-4/Claude**: 最佳
- **GPT-3.5**: 良好
- **本地模型**: 取决于模型大小

### **Q: 成本多少？**

A: 
- **Hermes 原生**: 计入当前会话（通常很便宜）
- **GPT-3.5**: ~$0.002/1K tokens
- **GPT-4**: ~$0.03/1K tokens
- **Ollama**: 免费

### **Q: 如何查看使用了哪个 API？**

A: 运行时会显示：
```
💡 尝试使用当前 Hermes Agent 的 API...
   🤖 委托给当前 Hermes Agent 生成摘要...
✅ 摘要生成成功！
```

或：
```
💡 检测到 OpenAI API Key，使用 OpenAI API...
```

---

## 🎯 总结

**Infinity Context LLM 摘要生成器**的核心优势：

1. **🎁 零配置** - 在 Hermes 中直接使用
2. **🤖 智能检测** - 自动选择最佳 API
3. **🔧 灵活部署** - 支持云端/本地多种方案
4. **📊 高质量** - LLM 生成，智能精炼
5. **💰 低成本** - 优先使用免费/现有资源

**立即开始使用吧！** 🚀

---

**Made with ❤️ by the Infinity Context Team**

*"Infinite context, small model"*
