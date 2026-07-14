# 🔄 Session Rotation - 自动触发配置

**让 Hermes Agent 自动调用 Session Rotation Skill**

---

## 🎯 目标

让 Hermes Agent 在**每次对话前**自动检查会话使用率，超过 80% 自动切换。

---

## 📋 配置方法

### **方法 1: 添加到 Hermes System Prompt（推荐）**

在 Hermes 的 system prompt 中添加：

```markdown
## Session Rotation - 自动会话管理

**每次对话前，自动执行以下检查**:

1. 检查当前会话使用率是否超过 80%
2. 如果超过，且最后一条消息是自然断点（"好的"、"谢谢"等）
3. 自动调用：`~/.hermes/scripts/session-rotation/session_rotator.sh check`
4. 根据结果决定是否切换

**自然断点关键词**:
- 中文：好的、明白了、谢谢、理解了
- 英文：ok, good, thanks, understood
- 表情：👌, ✅, 🙏

**如果用户主动说**：
- "切换" → 立即执行切换
- "压缩对话" → 生成摘要
- "继续" → 加载摘要
```

### **方法 2: 使用 Hermes Hook**

创建 `~/.hermes/hooks/before_response.sh`:

```bash
#!/bin/bash
# Hermes Hook - 每次响应前执行

# 检查 Session Rotation
~/.hermes/scripts/session-rotation/session_rotator.sh check 2>&1 | logger -t session-rotation
```

赋予执行权限：
```bash
chmod +x ~/.hermes/hooks/before_response.sh
```

### **方法 3: 使用 Cron + 通知（当前方案）**

已有的 Cron Job：
- 每 5 分钟检查一次
- 超过阈值 → 发送通知
- 用户看到通知后可手动触发

**升级**: 添加自动执行逻辑

```bash
# 在 cron 脚本中添加
if [ "$usage_rate" -ge "0.8" ] && [ "$is_natural_break" = true ]; then
    # 自动执行切换
    ~/.hermes/scripts/session-rotation/session_rotator.sh force
fi
```

---

## 🔧 当前状态

### **✅ 已完成**
- [x] Session Rotation Skill 已创建
- [x] 纯终端命令脚本已编写
- [x] Cron Job 已部署（每 5 分钟）
- [x] 摘要已生成（pending_summary.json）

### **⏳ 待完成**
- [ ] Hermes 自动触发配置
- [ ] Computer Use 权限配置
- [ ] 自动执行 /new 测试

---

## 🚀 立即测试

### **手动触发测试**

```bash
# 检查当前状态
~/.hermes/scripts/session-rotation/session_rotator.sh check

# 强制切换（不等待自然断点）
~/.hermes/scripts/session-rotation/session_rotator.sh force

# 查看摘要
cat ~/.hermes/session-rotation/pending_summary.json | jq .
```

### **验证 Computer Use**

```bash
# 测试 xdotool
which xdotool && echo "✅ xdotool 可用" || echo "❌ xdotool 不可用"

# 测试 tmux
which tmux && echo "✅ tmux 可用" || echo "❌ tmux 不可用"
```

---

## 📊 当前会话状态

根据 Cron 报告：
- **使用率**: 120% ⚠️（超过阈值）
- **消息数**: 195 轮
- **Token**: ~120,000
- **状态**: pending（有待处理摘要）

**建议**: 立即执行一次手动切换测试

```bash
~/.hermes/scripts/session-rotation/session_rotator.sh force
```

---

## 🎯 下一步

1. **立即**: 手动执行一次切换，验证流程
2. **今天**: 配置 Hermes 自动触发
3. **明天**: 测试 Computer Use 自动执行
4. **本周**: 完善自然断点检测

---

*Session Rotation Auto-Trigger Config v1.0.0*
