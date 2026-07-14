# 🔄 Session Rotation - Hermes 自动触发配置

**让 Hermes Agent 在每次对话前自动检查会话使用率**

---

## 🎯 配置目标

Hermes Agent 在**每次响应前**自动：
1. 检查会话使用率
2. 超过 80% → 自动切换
3. 使用 `computer_use` 执行 `/new`
4. 用户完全无感知

---

## 📋 配置步骤

### **Step 1: 创建 Hermes Hook 脚本**

创建 `~/.hermes/hooks/before_response.sh`:

```bash
#!/bin/bash
# Hermes Hook - 每次响应前自动检查 Session Rotation

set -e

SESSION_DIR="$HOME/.hermes/session-rotation"
SUMMARY_FILE="$SESSION_DIR/auto_summary.json"

# 检查是否有待处理的摘要
if [ -f "$SUMMARY_FILE" ]; then
    # 有待处理摘要，说明刚完成切换
    exit 0
fi

# 调用 Session Rotation 检查脚本
~/.hermes/scripts/session-rotation/session_rotator.sh check 2>&1 | logger -t session-rotation

exit 0
```

赋予执行权限：
```bash
chmod +x ~/.hermes/hooks/before_response.sh
```

---

### **Step 2: 配置 Hermes System Prompt**

在 Hermes 的 system prompt 或 instructions 中添加：

```markdown
## 🔄 Session Rotation - 自动会话管理

**重要**: 你是 Session Rotation 的一部分，负责自动会话管理。

### 每次对话前的检查流程

1. **检查使用率**:
   - 调用 `session_search(limit=1)` 获取当前会话
   - 计算 Token 使用率
   - 如果 > 80%，准备切换

2. **检测自然断点**:
   - 检查最后一条消息是否包含：
     - 中文：好的、明白了、谢谢、理解了
     - 英文：ok, good, thanks, understood
     - 表情：👌, ✅, 🙏
   - 如果是自然断点 → 执行切换

3. **执行自动切换**:
   ```python
   from hermes_tools import computer_use, send_message
   
   # 执行 /new
   computer_use.click_element("输入框")
   computer_use.type_text("/new")
   computer_use.press_key("Enter")
   
   # 等待新会话
   time.sleep(2)
   
   # 注入摘要
   send_message("📋 已自动恢复上下文...")
   ```

4. **事后通知**:
   ```python
   send_message("✅ 已自动切换到新会话，上下文已保留")
   ```

### 用户命令

响应用户的以下命令：
- **"切换"** → 立即执行切换
- **"压缩对话"** → 生成摘要
- **"继续"** → 加载摘要
- **"状态"** → 显示当前使用率

### 降级方案

如果 `computer_use` 不可用：
- 发送提示："请手动执行 `/new`"
- 等待用户执行后注入摘要

---

**记住**: 你的目标是让用户**完全无感知**地延续对话！
```

---

### **Step 3: 测试自动触发**

#### **测试 1: 手动触发检查**

```bash
# 运行检查脚本
~/.hermes/scripts/session-rotation/session_rotator.sh check

# 预期输出：
# [INFO] 检查会话使用率...
# [INFO] 会话：xxx
# [INFO] 消息数：195
# [INFO] Token 数：~120,000
# [INFO] 使用率：120.0%
# [WARNING] 使用率超过阈值，准备自动切换...
```

#### **测试 2: 强制切换**

```bash
# 强制切换（不等待自然断点）
~/.hermes/scripts/session-rotation/session_rotator.sh force

# 预期：
# - 生成摘要
# - 执行 /new（通过 xdotool 或 tmux）
# - 注入摘要
# - 发送通知
```

#### **测试 3: 验证 Computer Use**

```bash
# 检查 xdotool
which xdotool && echo "✅ xdotool 可用" || echo "❌ xdotool 不可用"

# 检查 tmux
which tmux && echo "✅ tmux 可用" || echo "❌ tmux 不可用"
```

---

### **Step 4: 验证配置**

#### **验证 Hook 是否生效**

```bash
# 查看 Hook 日志
journalctl -t session-rotation -f

# 或查看系统日志
tail -f /var/log/syslog | grep session-rotation
```

#### **验证 Hermes 是否自动调用**

1. 与 Hermes 对话
2. 观察是否自动检查使用率
3. 超过 80% 时是否自动切换

---

## 🔧 当前状态

### **✅ 已完成**
- [x] Session Rotation Skill 已创建
- [x] 纯终端命令脚本已编写 (`session_rotator.sh`)
- [x] Cron Job 已部署（每 5 分钟）
- [x] 摘要已生成（`pending_summary.json`）
- [x] 使用率检测正常（120% ⚠️）

### **⏳ 进行中**
- [x] 创建 Hook 脚本
- [ ] 配置 Hermes System Prompt
- [ ] 测试自动触发

### **❌ 待完成**
- [ ] Computer Use 权限配置
- [ ] 自动执行 /new 测试
- [ ] 自然断点检测优化

---

## 🚀 **立即执行**

### **选项 A: 使用 Hook（推荐）**

```bash
# 创建 Hook 脚本
cat > ~/.hermes/hooks/before_response.sh << 'EOF'
#!/bin/bash
# Hermes Hook - 每次响应前自动检查

~/.hermes/scripts/session-rotation/session_rotator.sh check 2>&1 | logger -t session-rotation
EOF

chmod +x ~/.hermes/hooks/before_response.sh
echo "✅ Hook 已配置"
```

### **选项 B: 修改 Hermes Config**

编辑 `~/.hermes/config.yaml` 或 `~/.hermes/profiles/feishu/config.yaml`:

```yaml
# 添加 Session Rotation 配置
session_rotation:
  enabled: true
  auto_check: true
  threshold: 0.8
  natural_breaks:
    - "好的"
    - "明白了"
    - "谢谢"
    - "ok"
    - "thanks"
```

### **选项 C: 使用 Skill 自动加载**

在 `~/.hermes/profiles/feishu/skills/autonomous-ai-agents/session-rotation/SKILL.md` 中添加：

```markdown
## Auto-Trigger

This skill is automatically triggered before every Hermes Agent response.
```

---

## 📊 **预期效果**

### **用户视角**

```
用户：好的，明白了，谢谢！
AI: 👍

[后台自动检测]
[自动执行 /new]
[自动注入摘要]

用户：对了，还有一个问题...
AI: 好的，基于之前的讨论...
```

### **后台日志**

```
[INFO] Session Rotation check started
[INFO] Usage rate: 120.0%
[WARNING] Threshold exceeded
[SUCCESS] Natural break point detected: "谢谢"
[INFO] Executing auto-switch...
[SUCCESS] /new executed
[SUCCESS] Summary injected
[SUCCESS] Post-notification sent
```

---

## 🎯 **下一步**

1. ✅ **立即**: 创建 Hook 脚本
2. ✅ **5 分钟后**: 测试自动触发
3. ✅ **今天**: 验证 Computer Use 执行
4. ✅ **本周**: 优化自然断点检测

---

*Session Rotation Auto-Trigger Config v1.0.0*  
*"True Automation, Zero User Perception"*
