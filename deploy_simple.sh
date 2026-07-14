#!/bin/bash
# 🚀 Infinity Context v1.0.0 - 极简部署

set -e

echo "🚀 部署 Infinity Context v1.0.0..."

# 复制脚本
mkdir -p ~/.hermes/scripts/infinity-context
cp scripts/auto_rotate.py ~/.hermes/scripts/infinity-context/
chmod +x ~/.hermes/scripts/infinity-context/auto_rotate.py

echo "✅ 部署完成！"
echo ""
echo "📋 使用方法:"
echo "  自动监控：添加 Cron Job 每 5 分钟运行"
echo "  手动执行：~/.hermes/scripts/infinity-context/auto_rotate.py"
echo ""
echo "🎯 功能:"
echo "  - 自动检测 80% 阈值"
echo "  - 自动执行 /new"
echo "  - 自动注入摘要"
echo "  - 用户完全无感知"
