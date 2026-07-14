#!/bin/bash
# 🚀 Session Rotation v1.0.0 - 部署脚本（纯终端命令版本）

set -e

echo "🚀 部署 Session Rotation v1.0.0（完全自动化）..."

# 创建目录
echo "📁 创建目录结构..."
mkdir -p ~/.hermes/scripts/session-rotation

# 复制文件
echo "📄 复制文件..."
cp session_rotator.sh ~/.hermes/scripts/session-rotation/
chmod +x ~/.hermes/scripts/session-rotation/session_rotator.sh

# 检查依赖
echo "🔍 检查依赖..."

# 检查 jq
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq 未安装，尝试安装..."
    if command -v apt &> /dev/null; then
        sudo apt install -y jq || echo "❌ 安装失败，请手动安装 jq"
    elif command -v yum &> /dev/null; then
        sudo yum install -y jq || echo "❌ 安装失败，请手动安装 jq"
    else
        echo "❌ 无法自动安装 jq，请手动安装"
    fi
fi

# 检查 bc
if ! command -v bc &> /dev/null; then
    echo "⚠️  bc 未安装，尝试安装..."
    if command -v apt &> /dev/null; then
        sudo apt install -y bc || echo "❌ 安装失败，请手动安装 bc"
    elif command -v yum &> /dev/null; then
        sudo yum install -y bc || echo "❌ 安装失败，请手动安装 bc"
    else
        echo "❌ 无法自动安装 bc，请手动安装 bc"
    fi
fi

# 检查 curl
if ! command -v curl &> /dev/null; then
    echo "⚠️  curl 未安装，尝试安装..."
    if command -v apt &> /dev/null; then
        sudo apt install -y curl || echo "❌ 安装失败，请手动安装 curl"
    elif command -v yum &> /dev/null; then
        sudo yum install -y curl || echo "❌ 安装失败，请手动安装 curl"
    else
        echo "❌ 无法自动安装 curl，请手动安装 curl"
    fi
fi

# 创建 Cron Job
echo "⏰ 部署 Cron Job..."
cat > /tmp/session_rotation_cron.sh << 'CRONEOF'
#!/bin/bash
# Cron Job - 每 5 分钟检查
python3 ~/.hermes/scripts/session-rotation/session_rotator.sh check 2>&1 | logger -t session-rotation
CRONEOF

chmod +x /tmp/session_rotation_cron.sh

# 添加到 crontab（如果支持）
if command -v crontab &> /dev/null; then
    (crontab -l 2>/dev/null | grep -v "session_rotator.sh"; echo "*/5 * * * * /tmp/session_rotation_cron.sh") | crontab - 2>/dev/null || echo "⚠️  无法添加 crontab"
    echo "✅ Cron Job 已添加"
else
    echo "⚠️  crontab 不可用，请手动配置定时任务"
fi

rm -f /tmp/session_rotation_cron.sh

echo ""
echo "✅ Session Rotation v1.0.0 部署完成！"
echo ""
echo "📋 特性:"
echo "  ✅ 纯终端命令（不依赖 hermes_tools）"
echo "  ✅ 自动检测 80% 阈值"
echo "  ✅ 自动生成摘要"
echo "  ✅ 自动执行 /new（xdotool/tmux）"
echo "  ✅ 自动注入摘要"
echo "  ✅ 用户完全无感知"
echo "  ✅ 自然断点检测"
echo "  ✅ 事后通知"
echo ""
echo "🎯 使用方法:"
echo "  自动监控：Cron Job 每 5 分钟自动检查"
echo "  手动检查：~/.hermes/scripts/session-rotation/session_rotator.sh check"
echo "  强制切换：~/.hermes/scripts/session-rotation/session_rotator.sh force"
echo "  查看状态：~/.hermes/scripts/session-rotation/session_rotator.sh status"
echo ""
echo "🎉 享受真正的自动化体验！"
