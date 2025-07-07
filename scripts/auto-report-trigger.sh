#!/bin/bash
# Auto Daily Report Trigger
# 自動日報作成トリガースクリプト

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/agentdev_auto_report.log"

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 時間チェック関数
check_time_trigger() {
    local current_hour=$(date '+%H')
    local current_minute=$(date '+%M')
    
    # 4:30 AM チェック
    if [ "$current_hour" = "04" ] && [ "$current_minute" = "30" ]; then
        return 0  # トリガー条件に一致
    fi
    
    return 1  # トリガー条件に不一致
}

# Claude Codeプロセスチェック
check_claude_running() {
    if pgrep -f "claude" > /dev/null; then
        return 0  # Claude実行中
    fi
    return 1  # Claude停止中
}

# 日報作成実行
trigger_report_creation() {
    local trigger_type="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    log "Triggering daily report creation: $trigger_type"
    
    # 日報ディレクトリ確保
    mkdir -p "/mnt/c/AgentDev/daily-reports"
    
    # 作業ログ実行
    if [ -f "$SCRIPT_DIR/create-daily-report.py" ]; then
        python3 "$SCRIPT_DIR/create-daily-report.py" >> "$LOG_FILE" 2>&1
    fi
    
    # トリガーファイル作成（Claudeが検出用）
    local trigger_file="/mnt/c/AgentDev/daily-reports/.trigger-$(date '+%Y-%m-%d')"
    
    cat > "$trigger_file" << EOF
{
    "trigger_type": "$trigger_type",
    "timestamp": "$timestamp",
    "message": "Daily report creation requested",
    "claude_instruction": "Please create a comprehensive daily report using the template in CLAUDE.md"
}
EOF
    
    log "Trigger file created: $trigger_file"
    return 0
}

# トークン制限検出（簡易版）
check_token_limit() {
    # Claude Codeのレスポンス時間や一般的な制限パターンをチェック
    # 実際の実装では、Claude Codeの出力やレスポンス時間を監視
    
    local recent_errors=$(grep -c "rate limit\|token limit\|quota" "$LOG_FILE" 2>/dev/null || echo "0")
    
    if [ "$recent_errors" -gt 0 ]; then
        return 0  # 制限検出
    fi
    
    return 1  # 制限未検出
}

# メイン監視ループ
monitor_and_trigger() {
    log "Starting daily report monitoring..."
    
    while true; do
        # 時間トリガーチェック
        if check_time_trigger; then
            if check_claude_running; then
                trigger_report_creation "scheduled"
            else
                log "Scheduled trigger time reached, but Claude not running"
            fi
            # 1時間待機（同じ時間に重複実行防止）
            sleep 3600
        fi
        
        # トークン制限チェック
        if check_token_limit; then
            if check_claude_running; then
                trigger_report_creation "token_limit"
                log "Token limit detected, report triggered"
            fi
            # 30分待機（制限解除まで）
            sleep 1800
        fi
        
        # 1分間隔でチェック
        sleep 60
    done
}

# 手動トリガー
manual_trigger() {
    local trigger_type="${1:-manual}"
    
    log "Manual daily report trigger: $trigger_type"
    trigger_report_creation "$trigger_type"
    
    echo "📋 Daily report trigger activated"
    echo "🕐 Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "📁 Check: /mnt/c/AgentDev/daily-reports/"
    echo ""
    echo "Claude should now create the detailed report."
}

# ステータス表示
show_status() {
    echo "🤖 Auto Report Trigger Status"
    echo ""
    
    if pgrep -f "auto-report-trigger" > /dev/null; then
        echo "✅ Monitoring: ACTIVE"
    else
        echo "❌ Monitoring: INACTIVE"
    fi
    
    echo "📊 Next scheduled trigger: Tomorrow 04:30"
    echo "📝 Log file: $LOG_FILE"
    
    if [ -f "$LOG_FILE" ]; then
        local last_entry=$(tail -1 "$LOG_FILE" 2>/dev/null || echo "No entries")
        echo "📄 Last log: $last_entry"
    fi
    
    echo ""
    echo "Commands:"
    echo "  $0 start     - Start monitoring"
    echo "  $0 trigger   - Manual trigger"
    echo "  $0 stop      - Stop monitoring" 
}

# 監視停止
stop_monitoring() {
    local pids=$(pgrep -f "auto-report-trigger" || echo "")
    
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill
        log "Auto report monitoring stopped"
        echo "🛑 Monitoring stopped"
    else
        echo "⚠️  No monitoring process found"
    fi
}

# メイン処理
case "${1:-status}" in
    "start")
        if pgrep -f "auto-report-trigger" > /dev/null; then
            echo "⚠️  Monitoring already running"
        else
            echo "🚀 Starting auto report monitoring..."
            monitor_and_trigger &
            echo "✅ Monitoring started (PID: $!)"
        fi
        ;;
    "trigger")
        manual_trigger "${2:-manual}"
        ;;
    "stop")
        stop_monitoring
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {start|trigger|stop|status}"
        exit 1
        ;;
esac