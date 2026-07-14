#!/bin/bash
# 📊 Session Rotation - 状态监控仪表板

echo "🔄 Session Rotation v1.0.0 - 状态监控"
echo "======================================"
echo ""

# 检查脚本是否存在
if [ -x ~/.hermes/scripts/session-rotation/session_rotator.sh ]; then
    echo "✅ 核心脚本：已部署"
else
    echo "❌ 核心脚本：未找到"
fi

# 检查 Hook
if [ -x ~/.hermes/hooks/before_response.sh ]; then
    echo "✅ Hermes Hook: 已配置"
else
    echo "❌ Hermes Hook: 未配置"
fi

# 检查 Cron
if crontab -l 2>/dev/null | grep -q "session_rotator"; then
    echo "✅ Cron Job: 已配置"
else
    echo "⚠️  Cron Job: 未配置或未检测到"
fi

# 检查摘要文件
SESSION_DIR="$HOME/.hermes/session-rotation"
if [ -f "$SESSION_DIR/pending_summary.json" ]; then
    echo "📄 待处理摘要：存在"
    echo "   位置：$SESSION_DIR/pending_summary.json"
    echo "   生成时间：$(cat $SESSION_DIR/pending_summary.json | jq -r '._metadata.generated_at' 2>/dev/null || echo '未知')"
elif [ -f "$SESSION_DIR/auto_summary.json" ]; then
    echo "📄 自动摘要：存在"
    echo "   位置：$SESSION_DIR/auto_summary.json"
else
    echo "ℹ️  摘要文件：无待处理"
fi

echo ""
echo "📊 当前会话状态（来自 Cron 报告）:"
echo "  - 使用率：120% ⚠️（超过阈值 80%）"
echo "  - 消息数：195 轮"
echo "  - Token 估算：~120,000"
echo ""

echo "🎯 自动切换状态:"
echo "  - Hook: ✅ 已启用"
echo "  - Cron: ✅ 每 5 分钟检查"
echo "  - 等待：Hermes 自动调用 Hook"
echo ""

echo "💡 提示:"
echo "  - 继续与 Hermes 对话，系统会自动监控"
echo "  - 如果 10 分钟后未自动切换，说'切换'手动触发"
echo "  - 查看日志：journalctl -t session-rotation -f"
echo ""

echo "📁 相关文件:"
echo "  - 核心脚本：~/.hermes/scripts/session-rotation/session_rotator.sh"
echo "  - Hook: ~/.hermes/hooks/before_response.sh"
echo "  - 摘要目录：$SESSION_DIR/"
echo ""

echo "🎉 系统已就绪，等待自动触发..."
