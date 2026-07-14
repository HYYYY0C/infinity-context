#!/bin/bash
# 🚀 Session Rotation Phase 3 - 完全自动化部署脚本

set -e

echo "🚀 部署 Session Rotation Phase 3（完全自动化）..."

# 创建目录
echo "📁 创建目录结构..."
mkdir -p ~/.hermes/scripts/session-rotation-phase3

# 复制文件
echo "📄 复制文件..."
cp fully_auto_rotator.py ~/.hermes/scripts/session-rotation-phase3/

chmod +x ~/.hermes/scripts/session-rotation-phase3/fully_auto_rotator.py

# 创建 Cron Job
echo "⏰ 部署 Cron Job..."
cat > /tmp/phase3_cron_prompt.txt << 'EOF'
运行 Phase 3 完全自动化监控：

```bash
python3 ~/.hermes/scripts/session-rotation-phase3/fully_auto_rotator.py check
```

**Phase 3 特性**:
- 自动检测 80% 阈值
- 自动生成摘要
- 自动执行 /new（Computer Use）
- 自动注入摘要
- 用户完全无感知

如果用户说"强制切换"，执行：
```bash
python3 ~/.hermes/scripts/session-rotation-phase3/fully_auto_rotator.py force
```

如果用户说"状态"，执行：
```bash
python3 ~/.hermes/scripts/session-rotation-phase3/fully_auto_rotator.py status
```
EOF

hermes cron create \
  --name "Phase3-完全自动化" \
  --schedule "*/5 * * * *" \
  --prompt-file /tmp/phase3_cron_prompt.txt \
  2>/dev/null || echo "⚠️  Cron Job 可能已存在"

rm -f /tmp/phase3_cron_prompt.txt

echo ""
echo "✅ Phase 3 部署完成！"
echo ""
echo "📋 Phase 3 特性:"
echo "  ✅ 自动检测 80% 阈值"
echo "  ✅ 自动生成摘要"
echo "  ✅ 自动执行 /new（Computer Use）"
echo "  ✅ 自动注入摘要"
echo "  ✅ 用户完全无感知"
echo ""
echo "🎯 与 Phase 1 的区别:"
echo "  Phase 1: 一键切换（需用户点击）"
echo "  Phase 3: 完全自动（用户无感知）"
echo ""
echo "🎉 享受真正的自动化体验！"
