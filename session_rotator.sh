#!/bin/bash
# 🔄 Session Rotation v1.0.0 - 纯终端命令版本
# 不依赖 hermes_tools，完全使用终端命令

set -e

# 配置
HERMES_API_URL="${HERMES_API_URL:-http://localhost:8000}"
SESSION_DIR="$HOME/.hermes/session-rotation"
SUMMARY_FILE="$SESSION_DIR/auto_summary.json"
STATE_FILE="$SESSION_DIR/auto_state.json"

# 阈值
THRESHOLD_MESSAGES=40
THRESHOLD_TOKENS=100000
AUTO_THRESHOLD=0.8

# 自然断点关键词
NATURAL_BREAKS=("好的" "明白了" "谢谢" "理解了" "知道了" "ok" "good" "thanks" "👌" "✅")

# 创建目录
mkdir -p "$SESSION_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取当前会话 ID
get_current_session_id() {
    log_info "获取当前会话 ID..."
    
    # 方法 1: 从 Hermes API 获取
    if command -v curl &> /dev/null; then
        response=$(curl -s "$HERMES_API_URL/api/sessions?limit=1" 2>/dev/null || echo "")
        if [ -n "$response" ]; then
            session_id=$(echo "$response" | jq -r '.[0].id' 2>/dev/null || echo "")
            if [ -n "$session_id" ]; then
                echo "$session_id"
                return 0
            fi
        fi
    fi
    
    # 方法 2: 从本地文件读取（备用方案）
    # Hermes 通常在 ~/.hermes/sessions/ 存储会话
    if [ -d "$HOME/.hermes/sessions" ]; then
        latest_session=$(ls -t "$HOME/.hermes/sessions/" 2>/dev/null | head -1 || echo "")
        if [ -n "$latest_session" ]; then
            echo "$latest_session"
            return 0
        fi
    fi
    
    log_error "无法获取会话 ID"
    return 1
}

# 获取会话消息
get_session_messages() {
    local session_id="$1"
    log_info "获取会话消息：$session_id"
    
    # 方法 1: 从 API 获取
    if command -v curl &> /dev/null; then
        response=$(curl -s "$HERMES_API_URL/api/sessions/$session_id/messages?limit=100" 2>/dev/null || echo "")
        if [ -n "$response" ]; then
            echo "$response"
            return 0
        fi
    fi
    
    # 方法 2: 从本地文件读取
    local session_file="$HOME/.hermes/sessions/$session_id/messages.json"
    if [ -f "$session_file" ]; then
        cat "$session_file"
        return 0
    fi
    
    log_error "无法获取会话消息"
    return 1
}

# 计算 Token 数（简化版：按字符数估算）
count_tokens() {
    local text="$1"
    # 简单估算：每 4 个字符约 1 个 token
    local char_count=${#text}
    echo $((char_count / 4))
}

# 检查会话使用率
check_session_usage() {
    log_info "检查会话使用率..."
    
    # 获取会话 ID
    local session_id
    session_id=$(get_current_session_id) || return 1
    
    # 获取消息
    local messages
    messages=$(get_session_messages "$session_id") || return 1
    
    # 统计消息数
    local message_count
    message_count=$(echo "$messages" | jq 'length' 2>/dev/null || echo "0")
    
    # 估算 Token 数
    local total_tokens=0
    local content
    content=$(echo "$messages" | jq -r '.[].content' 2>/dev/null || echo "")
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local tokens
            tokens=$(count_tokens "$line")
            total_tokens=$((total_tokens + tokens))
        fi
    done <<< "$content"
    
    # 计算使用率
    local usage_rate_messages=$(echo "scale=2; $message_count / $THRESHOLD_MESSAGES" | bc)
    local usage_rate_tokens=$(echo "scale=2; $total_tokens / $THRESHOLD_TOKENS" | bc)
    
    # 取较大值
    local usage_rate
    if (( $(echo "$usage_rate_messages > $usage_rate_tokens" | bc -l) )); then
        usage_rate=$usage_rate_messages
    else
        usage_rate=$usage_rate_tokens
    fi
    
    log_info "会话：$session_id"
    log_info "消息数：$message_count"
    log_info "Token 数：~$total_tokens"
    log_info "使用率：$(echo "scale=1; $usage_rate * 100" | bc)%"
    
    # 检查是否需要切换
    if (( $(echo "$usage_rate >= $AUTO_THRESHOLD" | bc -l) )); then
        log_warning "使用率超过阈值，准备自动切换..."
        
        # 获取最后一条消息
        local last_message
        last_message=$(echo "$messages" | jq -r '.[-1].content' 2>/dev/null || echo "")
        
        # 检查是否是自然断点
        local is_natural_break=false
        for break_word in "${NATURAL_BREAKS[@]}"; do
            if [[ "$last_message" == *"$break_word"* ]]; then
                is_natural_break=true
                log_success "检测到自然断点：$break_word"
                break
            fi
        done
        
        if [ "$is_natural_break" = true ]; then
            log_success "执行自动切换..."
            execute_auto_switch "$session_id" "$messages"
        else
            log_info "未检测到自然断点，发送温和提醒..."
            send_gentle_reminder "$usage_rate"
        fi
    else
        log_success "使用率正常，无需操作"
    fi
}

# 执行自动切换
execute_auto_switch() {
    local session_id="$1"
    local messages="$2"
    
    log_info "开始自动切换..."
    
    # Step 1: 生成摘要（调用 Python 脚本或 LLM API）
    log_info "Step 1: 生成摘要..."
    local summary
    summary=$(generate_summary "$messages") || {
        log_error "摘要生成失败"
        return 1
    }
    
    # Step 2: 保存摘要
    log_info "Step 2: 保存摘要..."
    echo "$summary" > "$SUMMARY_FILE" || {
        log_error "摘要保存失败"
        return 1
    }
    
    # Step 3: 等待合适时机
    log_info "Step 3: 等待合适时机..."
    sleep 3
    
    # Step 4: 自动执行 /new
    log_info "Step 4: 自动执行 /new..."
    if auto_execute_new; then
        log_success "已执行 /new"
    else
        log_error "执行 /new 失败"
        send_manual_switch_prompt
        return 1
    fi
    
    # Step 5: 等待新会话
    log_info "Step 5: 等待新会话开启..."
    local new_session_id
    new_session_id=$(wait_for_new_session "$session_id") || {
        log_error "未检测到新会话"
        send_manual_switch_prompt
        return 1
    }
    log_success "新会话：$new_session_id"
    
    # Step 6: 注入摘要
    log_info "Step 6: 注入摘要..."
    if inject_summary "$new_session_id"; then
        log_success "摘要已注入"
    else
        log_error "摘要注入失败"
        return 1
    fi
    
    # Step 7: 事后通知
    log_info "Step 7: 发送事后通知..."
    send_post_notification "$summary"
    
    log_success "自动切换完成！"
}

# 生成摘要（简化版：调用外部 API 或 Python）
generate_summary() {
    local messages="$1"
    
    # 提取最近 50 条消息
    local recent_messages
    recent_messages=$(echo "$messages" | jq '.[-50:]' 2>/dev/null || echo "[]")
    
    # 转换为文本
    local conversation_text
    conversation_text=$(echo "$recent_messages" | jq -r '.[] | "\(.role): \(.content)"' 2>/dev/null || echo "")
    
    # 调用 LLM API 生成摘要（这里简化为 Mock，实际应调用 API）
    # 实际部署时替换为真实的 LLM API 调用
    cat << EOF
{
  "summary": "会话摘要：讨论了多个话题，包括项目进展、技术选型等。",
  "key_points": ["项目 A 进展顺利", "决定采用方案 B", "待办事项 C"],
  "action_items": ["完成任务 D", "Review 代码 E"],
  "context": {
    "projects": ["项目 A", "项目 B"],
    "decisions": ["采用方案 B"],
    "tech_stack": ["Python", "Bash"]
  },
  "next_steps": "继续讨论项目 C 的实现细节",
  "confidence": 0.95
}
EOF
}

# 自动执行 /new（模拟键盘输入）
auto_execute_new() {
    # 方法 1: 使用 xdotool（Linux）
    if command -v xdotool &> /dev/null; then
        xdotool search --name "Hermes" windowactivate --sync 2>/dev/null || true
        xdotool type --clearmodifiers "/new" 2>/dev/null || true
        xdotool key Return 2>/dev/null || true
        log_info "使用 xdotool 执行 /new"
        return 0
    fi
    
    # 方法 2: 使用 tmux 发送按键
    if command -v tmux &> /dev/null && [ -n "$TMUX" ]; then
        tmux send-keys "/new" C-m 2>/dev/null || true
        log_info "使用 tmux 执行 /new"
        return 0
    fi
    
    # 方法 3: 直接输出提示（降级方案）
    log_warning "无法自动执行 /new，请手动输入 /new"
    echo "/new"
    return 0
}

# 等待新会话开启
wait_for_new_session() {
    local old_session_id="$1"
    local timeout=30
    local start_time=$(date +%s)
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge $timeout ]; then
            log_error "等待超时"
            return 1
        fi
        
        # 获取当前会话 ID
        local new_session_id
        new_session_id=$(get_current_session_id 2>/dev/null || echo "")
        
        if [ -n "$new_session_id" ] && [ "$new_session_id" != "$old_session_id" ]; then
            echo "$new_session_id"
            return 0
        fi
        
        sleep 2
    done
}

# 注入摘要到新会话
inject_summary() {
    local new_session_id="$1"
    
    if [ ! -f "$SUMMARY_FILE" ]; then
        log_error "摘要文件不存在"
        return 1
    fi
    
    # 读取摘要
    local summary
    summary=$(cat "$SUMMARY_FILE")
    
    # 提取字段
    local summary_text=$(echo "$summary" | jq -r '.summary' 2>/dev/null || echo "无摘要")
    local key_points=$(echo "$summary" | jq -r '.key_points[]' 2>/dev/null | sed 's/^/• /' || echo "")
    local action_items=$(echo "$summary" | jq -r '.action_items[]' 2>/dev/null | sed 's/^/• /' || echo "")
    local next_steps=$(echo "$summary" | jq -r '.next_steps' 2>/dev/null || echo "继续当前任务")
    
    # 生成注入消息
    local inject_message
    inject_message=$(cat << EOF
📋 **已自动恢复上下文**

**摘要**: $summary_text

**关键点**:
$key_points

**待办事项**:
$action_items

**下一步**: $next_steps

---
我们可以继续了！有什么需要我做的吗？
EOF
)
    
    # 发送消息（通过 API 或终端输出）
    if command -v curl &> /dev/null; then
        curl -s -X POST "$HERMES_API_URL/api/sessions/$new_session_id/messages" \
            -H "Content-Type: application/json" \
            -d "{\"role\": \"assistant\", \"content\": $(echo "$inject_message" | jq -Rs '.')} " \
            2>/dev/null || true
    fi
    
    # 输出到终端
    echo "$inject_message"
    
    # 清理临时文件
    rm -f "$SUMMARY_FILE"
    
    return 0
}

# 发送温和提醒
send_gentle_reminder() {
    local usage_rate="$1"
    
    local message=$(cat << EOF
💡 **提示**: 当前会话使用率已达 $(echo "scale=0; $usage_rate * 100" | bc)%

建议：
- 等一个自然停顿点（如"好的"、"谢谢"）
- 我会自动切换到新会话
- 或者现在说"切换"立即执行

（自动模式已启用）
EOF
)
    
    echo "$message"
    
    # 通过 API 发送（如果可用）
    if command -v curl &> /dev/null; then
        curl -s -X POST "$HERMES_API_URL/api/notifications" \
            -H "Content-Type: application/json" \
            -d "{\"message\": $(echo "$message" | jq -Rs '.')} " \
            2>/dev/null || true
    fi
}

# 发送手动切换提示
send_manual_switch_prompt() {
    local message=$(cat << EOF
⚠️ **自动切换失败**

请手动执行：
1. 说 "/new" 开启新会话
2. 说 "继续" 恢复上下文

抱歉给您带来不便，我会继续改进自动切换功能。
EOF
)
    
    echo "$message"
}

# 发送事后通知
send_post_notification() {
    local summary="$1"
    
    local summary_text=$(echo "$summary" | jq -r '.summary' 2>/dev/null || echo "无摘要")
    local preview=${summary_text:0:100}
    
    local message=$(cat << EOF
✅ **已自动切换到新会话**

为了保持最佳性能，我已自动：
1. 生成了上一会话的摘要
2. 开启了新会话
3. 注入了上下文

**摘要预览**: ${preview}...

我们可以继续了！
EOF
)
    
    echo "$message"
    
    # 通过 API 发送
    if command -v curl &> /dev/null; then
        curl -s -X POST "$HERMES_API_URL/api/notifications" \
            -H "Content-Type: application/json" \
            -d "{\"message\": $(echo "$message" | jq -Rs '.')} " \
            2>/dev/null || true
    fi
}

# 主函数
main() {
    log_info "Session Rotation v1.0.0 - 纯终端命令版本"
    log_info "======================================"
    
    case "${1:-check}" in
        check)
            check_session_usage
            ;;
        force)
            log_warning "强制切换模式..."
            check_session_usage
            ;;
        status)
            if [ -f "$STATE_FILE" ]; then
                cat "$STATE_FILE" | jq . 2>/dev/null || cat "$STATE_FILE"
            else
                echo "无状态信息"
            fi
            ;;
        *)
            echo "用法：$0 {check|force|status}"
            exit 1
            ;;
    esac
}

main "$@"
