#!/usr/bin/env bash
#
# run-dev-loop.sh — 自动化 Claude Code 开发循环
#
# 用法:
#   ./scripts/run-dev-loop.sh <次数>
#   ./scripts/run-dev-loop.sh 10        # 运行10轮开发周期
#
# 每轮会:
#   1. 从 tasks.md 中找到下一个未完成的任务
#   2. 调用 Claude Code 执行该任务
#   3. Claude 自动完成实现、标记任务完成、提交 commit
#   4. 记录日志
#

set -euo pipefail

# ─── 颜色定义 ───────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── 参数解析 ───────────────────────────────────────────
if [ $# -lt 1 ]; then
    echo -e "${RED}错误: 缺少参数${NC}"
    echo ""
    echo "用法: $0 <次数>"
    echo "  <次数>  要运行的开发周期数量"
    echo ""
    echo "示例:"
    echo "  $0 10     # 运行10轮开发周期"
    echo "  $0 5      # 运行5轮开发周期"
    exit 1
fi

TOTAL_RUNS=$1

if ! [[ "$TOTAL_RUNS" =~ ^[0-9]+$ ]] || [ "$TOTAL_RUNS" -lt 1 ]; then
    echo -e "${RED}错误: 参数必须是正整数，收到: $TOTAL_RUNS${NC}"
    exit 1
fi

# ─── 路径配置 ───────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TASKS_FILE="$PROJECT_ROOT/specs/001-ai-editorial-pipeline/tasks.md"
LOG_DIR="$PROJECT_ROOT/logs/dev-loop"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/run_${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

# ─── 日志函数 ───────────────────────────────────────────
log() {
    local level="$1"
    shift
    local msg="$*"
    local ts
    ts=$(date +"%Y-%m-%d %H:%M:%S")
    echo -e "[$ts] [$level] $msg" | tee -a "$LOG_FILE"
}

log_info()    { log "${BLUE}INFO${NC}"    "$*"; }
log_success() { log "${GREEN}SUCCESS${NC}" "$*"; }
log_warn()    { log "${YELLOW}WARN${NC}"   "$*"; }
log_error()   { log "${RED}ERROR${NC}"     "$*"; }

# ─── 任务检测函数 ───────────────────────────────────────
get_next_task() {
    # 从 tasks.md 中找到第一个未完成的任务 (- [ ] Txxx ...)
    if [ ! -f "$TASKS_FILE" ]; then
        echo ""
        return
    fi
    grep -n '^\- \[ \] T[0-9]\+' "$TASKS_FILE" | head -1 | sed 's/^[0-9]*://'
}

get_task_id() {
    echo "$1" | grep -o 'T[0-9]\+' | head -1
}

count_remaining_tasks() {
    if [ ! -f "$TASKS_FILE" ]; then
        echo "0"
        return
    fi
    grep -c '^\- \[ \] T[0-9]\+' "$TASKS_FILE" 2>/dev/null || echo "0"
}

count_completed_tasks() {
    if [ ! -f "$TASKS_FILE" ]; then
        echo "0"
        return
    fi
    grep -c '^\- \[[xX]\] T[0-9]\+' "$TASKS_FILE" 2>/dev/null || echo "0"
}

# ─── Claude Code 调用 Prompt ────────────────────────────
CLAUDE_PROMPT='You are working on the AI Editorial Pipeline project. Follow these steps precisely:

1. Read the tasks file at specs/001-ai-editorial-pipeline/tasks.md
2. Find the FIRST uncompleted task (line starting with "- [ ] T...")
3. Read the implementation plan at specs/001-ai-editorial-pipeline/plan.md for project structure and tech stack
4. Read specs/001-ai-editorial-pipeline/data-model.md and specs/001-ai-editorial-pipeline/contracts/openapi.yaml if the task needs entity or API details
5. Implement the task completely:
   - Create/modify all necessary files with production-quality code
   - Follow the project constitution at .specify/memory/constitution.md
   - Ensure code passes linting standards
   - Add all necessary imports and dependencies
6. After implementation, mark the task as done in tasks.md by changing "- [ ]" to "- [x]" for that specific task
7. Git commit the changes with a conventional commit message: "feat: <task-id> <brief description>"
8. Output a brief summary of what was done

IMPORTANT: Only work on ONE task per session. Do not skip tasks. Do not work on tasks that are already marked [x]. Work in order.'

# ─── 主循环 ─────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          AI Editorial Pipeline — 自动开发循环               ║${NC}"
echo -e "${CYAN}║          计划运行: ${TOTAL_RUNS} 轮                                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "日志文件: $LOG_FILE"
log_info "任务文件: $TASKS_FILE"
log_info "计划运行 $TOTAL_RUNS 轮开发周期"
echo ""

COMPLETED=0
FAILED=0
SKIPPED=0
START_TIME=$(date +%s)

for ((i = 1; i <= TOTAL_RUNS; i++)); do
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "🔄 轮次 $i / $TOTAL_RUNS"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # 检查剩余任务
    REMAINING=$(count_remaining_tasks)
    DONE=$(count_completed_tasks)
    log_info "任务进度: 已完成 $DONE | 剩余 $REMAINING"

    if [ "$REMAINING" -eq 0 ]; then
        log_success "🎉 所有任务已完成! 无需继续运行。"
        break
    fi

    # 获取下一个任务
    NEXT_TASK=$(get_next_task)
    TASK_ID=$(get_task_id "$NEXT_TASK")

    if [ -z "$TASK_ID" ]; then
        log_warn "无法解析下一个任务ID，跳过本轮"
        SKIPPED=$((SKIPPED + 1))
        continue
    fi

    log_info "📋 当前任务: $TASK_ID"
    log_info "📝 任务内容: $(echo "$NEXT_TASK" | sed 's/^- \[ \] //')"

    # 调用 Claude Code
    ITER_START=$(date +%s)
    log_info "🤖 正在调用 Claude Code..."

    set +e
    claude --dangerously-skip-permissions \
           -p "$CLAUDE_PROMPT" \
           --output-format text \
           2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=$?
    set -e

    ITER_END=$(date +%s)
    ITER_DURATION=$((ITER_END - ITER_START))

    if [ $EXIT_CODE -eq 0 ]; then
        # 验证任务是否真的被标记完成了
        NEW_REMAINING=$(count_remaining_tasks)
        if [ "$NEW_REMAINING" -lt "$REMAINING" ]; then
            log_success "✅ $TASK_ID 完成 (耗时 ${ITER_DURATION}s)"
            COMPLETED=$((COMPLETED + 1))
        else
            log_warn "⚠️  Claude 退出码为0但任务 $TASK_ID 未被标记完成"
            FAILED=$((FAILED + 1))
        fi
    else
        log_error "❌ $TASK_ID 失败 (退出码: $EXIT_CODE, 耗时 ${ITER_DURATION}s)"
        FAILED=$((FAILED + 1))
    fi

    # 轮次间统计
    log_info "本轮统计: 成功=$COMPLETED 失败=$FAILED 跳过=$SKIPPED"

    # 轮次间短暂暂停，避免API速率限制
    if [ "$i" -lt "$TOTAL_RUNS" ]; then
        log_info "⏳ 等待 5 秒后开始下一轮..."
        sleep 5
    fi
done

# ─── 最终报告 ───────────────────────────────────────────
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
TOTAL_MINUTES=$((TOTAL_DURATION / 60))
TOTAL_SECONDS=$((TOTAL_DURATION % 60))

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                    运行结果报告                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
log_info "总耗时: ${TOTAL_MINUTES}分${TOTAL_SECONDS}秒"
log_info "计划轮次: $TOTAL_RUNS"
log_success "成功: $COMPLETED"
[ "$FAILED" -gt 0 ] && log_error "失败: $FAILED" || log_info "失败: 0"
[ "$SKIPPED" -gt 0 ] && log_warn "跳过: $SKIPPED" || log_info "跳过: 0"
echo ""

FINAL_DONE=$(count_completed_tasks)
FINAL_REMAINING=$(count_remaining_tasks)
log_info "最终任务进度: 已完成 $FINAL_DONE | 剩余 $FINAL_REMAINING"

if [ "$FINAL_REMAINING" -eq 0 ]; then
    log_success "🎉 所有任务已完成!"
else
    log_info "💡 继续运行: $0 $FINAL_REMAINING"
fi

echo ""
log_info "完整日志: $LOG_FILE"
