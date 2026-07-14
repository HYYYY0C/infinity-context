# Infinity Context 配置示例

## Hermes Agent 配置

Infinity Context 需要 Hermes Agent 环境才能运行。以下是推荐的配置：

### **环境变量**

```bash
# Hermes API 配置（如果需要）
export HERMES_API_URL="http://localhost:8000"
export HERMES_API_KEY="your-api-key-here"

# LLM 配置（用于摘要生成）
export LLM_PROVIDER="hermes"  # 或 "openai", "anthropic", "ollama"
export LLM_MODEL="claude-sonnet-4"  # 根据提供商选择
```

### **Hermes Skills 配置**

确保以下 Skills 已启用：

- ✅ `session_search` - 读取会话历史
- ✅ `computer_use` - 模拟用户输入
- ✅ `send_message` - 发送消息
- ✅ `delegate_task` - 调用 LLM 生成摘要

---

## tiktoken 配置

### **安装**

```bash
pip install tiktoken
```

### **模型编码映射**

```python
# 在 auto_rotate.py 中配置
MODEL_ENCODINGS = {
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "claude-3": "cl100k_base",
    "claude-sonnet-4": "cl100k_base",
    "llama-3": "cl100k_base",
}

# 选择正确的编码
encoding_name = MODEL_ENCODINGS.get(model_name, "cl100k_base")
encoding = tiktoken.get_encoding(encoding_name)
```

---

## 阈值配置

### **推荐设置**

```python
# 使用率阈值（80% 触发）
USAGE_THRESHOLD = 0.8

# Token 限制（根据模型调整）
TOKEN_LIMIT = 128000  # Claude 3 / GPT-4
# TOKEN_LIMIT = 16000  # GPT-3.5-turbo
# TOKEN_LIMIT = 200000  # Claude 3 200K

# 检查间隔（秒）
CHECK_INTERVAL = 300  # 5 分钟
```

### **自定义阈值**

根据你的使用场景调整：

```python
# 保守模式（更早切换）
USAGE_THRESHOLD = 0.7

# 激进模式（更晚切换）
USAGE_THRESHOLD = 0.9

# 生产环境（推荐）
USAGE_THRESHOLD = 0.8
```

---

## 降级方案配置

### **computer_use 不可用时**

如果 `computer_use` 在你的环境中不可用，可以配置降级方案：

```python
# 在 auto_rotate.py 中
FALLBACK_MODE = "manual"  # 或 "notification_only"

if FALLBACK_MODE == "manual":
    # 提示用户手动执行 /new
    print("💡 请手动执行：/new")
elif FALLBACK_MODE == "notification_only":
    # 只发送通知，不执行任何操作
    send_message("⚠️  使用率超过阈值，请考虑切换会话")
```

### **LLM API 不可用时**

如果 LLM API 不可用，使用模板摘要：

```python
# 降级到模板摘要
summary_text = f"""
会话摘要：
- 总轮数：{len(messages)}
- 最近话题：{last_topic}
- 待办事项：{pending_tasks}
"""
```

---

## 日志配置

### **启用详细日志**

```bash
# 设置日志级别
export LOG_LEVEL="DEBUG"  # 或 "INFO", "WARNING", "ERROR"
```

### **日志文件**

```python
# 在 auto_rotate.py 中配置日志
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/infinity-context.log'),
        logging.StreamHandler()
    ]
)
```

---

## 性能优化

### **缓存配置**

```python
# 缓存摘要结果（避免重复生成）
from functools import lru_cache

@lru_cache(maxsize=100)
def generate_summary_cached(messages_hash: str) -> str:
    """缓存的摘要生成"""
    ...
```

### **批量处理**

```python
# 批量处理消息（减少 API 调用）
BATCH_SIZE = 50

for i in range(0, len(messages), BATCH_SIZE):
    batch = messages[i:i+BATCH_SIZE]
    process_batch(batch)
```

---

## 安全配置

### **API Key 管理**

```bash
# ✅ 好的做法：使用环境变量
export HERMES_API_KEY="your-key-here"

# ❌ 避免：硬编码在代码中
API_KEY = "your-key-here"  # 不要这样做！
```

### **敏感信息**

```python
# 在日志中脱敏
def sanitize_key(key: str) -> str:
    """脱敏 API Key"""
    return key[:4] + "*" * (len(key) - 8) + key[-4:]

logger.info(f"Using API Key: {sanitize_key(api_key)}")
```

---

## 监控和告警

### **Prometheus 指标**

```python
# 导出指标供 Prometheus 抓取
from prometheus_client import Counter, Gauge, start_http_server

# 定义指标
SESSION_ROTATIONS = Counter('session_rotations_total', 'Total session rotations')
USAGE_RATE = Gauge('session_usage_rate', 'Current session usage rate')
SUMMARY_GENERATION_TIME = Gauge('summary_generation_seconds', 'Time to generate summary')

# 启动指标服务器
start_http_server(8000)
```

### **告警配置**

```yaml
# Prometheus alerting rules
groups:
- name: infinity-context
  rules:
  - alert: HighUsageRate
    expr: session_usage_rate > 0.9
    for: 5m
    annotations:
      summary: "会话使用率超过 90%"
```

---

## 故障排查

### **常见问题**

#### **问题 1: Token 计数不准确**

```bash
# 检查 tiktoken 版本
pip show tiktoken

# 升级到最新版本
pip install --upgrade tiktoken
```

#### **问题 2: computer_use 无法执行**

```bash
# 检查 Hermes 版本
hermes --version

# 确保 computer_use 已启用
hermes skills list
```

#### **问题 3: LLM 摘要生成失败**

```bash
# 检查 LLM API 连接
curl -X POST $LLM_API_URL/health

# 检查 API Key
echo $LLM_API_KEY
```

---

## 最佳实践

### **1. 定期备份配置**

```bash
# 备份配置文件
cp ~/.hermes/config.yaml ~/.hermes/config.yaml.backup.$(date +%Y%m%d)
```

### **2. 监控使用率趋势**

```python
# 记录使用率历史
usage_history = []
usage_history.append(usage_rate)

# 分析趋势
if len(usage_history) > 10:
    trend = usage_history[-1] - usage_history[0]
    if trend > 0.2:
        print("⚠️  使用率快速增长")
```

### **3. 定期清理旧会话**

```bash
# 清理超过 30 天的会话
hermes sessions cleanup --older-than 30d
```

---

## 获取帮助

- 📚 [README.md](README.md) - 完整文档
- 🐛 [GitHub Issues](https://github.com/HYYYY0C/infinity-context/issues) - 报告问题
- 💬 [GitHub Discussions](https://github.com/HYYYY0C/infinity-context/discussions) - 讨论和交流

---

*"Infinite context, small model"*
