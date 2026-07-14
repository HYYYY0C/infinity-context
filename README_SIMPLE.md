# 🔄 Infinity Context v1.0.0

**小模型，长上下文**

让 128K 模型获得 1M+ 连续对话体验，完全自动化！

---

## 🎯 唯一目标

**小模型，长上下文**

- ❌ 不做复杂功能
- ❌ 不要手动操作
- ✅ **自动检测、自动切换、自动恢复**

---

## 🚀 快速开始

```bash
git clone https://github.com/HYYYY0C/infinity-context.git
cd infinity-context
bash deploy_simple.sh
```

**就这么简单！**

---

## ⚠️ 系统要求

### **必需**
- ✅ Hermes Agent 环境（支持 `session_search`, `computer_use`, `send_message`）
- ✅ Python 3.8+
- ✅ `tiktoken` 库（`pip install tiktoken`）

### **重要说明**
- ⚠️ **本工具依赖 Hermes Agent 运行时**，无法在独立 Python 环境中运行
- ⚠️ **`computer_use` 需要 Hermes 支持 GUI 自动化**，某些环境可能不可用
- ⚠️ **摘要生成依赖 LLM API**，需要配置有效的模型

### **降级方案**
如果 `computer_use` 不可用：
- 工具会提示手动执行 `/new`
- 摘要仍会生成并保存
- 用户手动注入摘要**

---

## 💡 工作原理

```
使用率 > 80%
    ↓
自动生成摘要
    ↓
自动执行 /new
    ↓
自动注入摘要
    ↓
用户继续对话（无感知）
```

---

## 📊 对比

| 版本 | 操作 | 体验 |
|------|------|------|
| **v0.3.0** | 手动复制 + CLI | 3 步操作 |
| **v1.0.0** | 完全自动 | **0 次操作** |

---

## 🔧 核心代码

只有**一个脚本**：`auto_rotate.py`

```python
# 检测使用率
if usage_rate > 0.8:
    # 生成摘要
    # 执行 /new
    # 注入摘要
```

**就这么简单！**

---

## 📝 更新日志

**v1.0.0** (2026-07-14) - 完全自动化
- ✅ 自动检测 80% 阈值
- ✅ 自动执行 /new
- ✅ 自动注入摘要
- ✅ 极简设计

**v0.3.0** (2026-07-14) - CLI 手动版
- 手动复制对话
- CLI 生成摘要

---

*"Infinite context, small model"*
