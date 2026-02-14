<#
.SYNOPSIS
    自动化 Claude Code 开发循环 (PowerShell版)

.DESCRIPTION
    在 for 循环中调用 Claude Code，每次执行一个开发任务。
    自动从 tasks.md 中取下一个未完成任务，完成实现并提交 commit。

.PARAMETER Runs
    要运行的开发周期数量

.EXAMPLE
    .\scripts\run-dev-loop.ps1 -Runs 10
    .\scripts\run-dev-loop.ps1 10
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateRange(1, 999)]
    [int]$Runs
)

$ErrorActionPreference = 'Continue'

# ─── 路径配置 ───────────────────────────────────────────
$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
$TasksFile = Join-Path $ProjectRoot "specs\001-ai-editorial-pipeline\tasks.md"
$LogDir = Join-Path $ProjectRoot "logs\dev-loop"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "run_${Timestamp}.log"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# ─── 日志函数 ───────────────────────────────────────────
function Write-Log {
    param(
        [string]$Level,
        [string]$Message,
        [string]$Color = "White"
    )
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $line = "[$ts] [$Level] $Message"
    Write-Host $line -ForegroundColor $Color
    Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

function Log-Info    { param([string]$Msg) Write-Log "INFO"    $Msg "Cyan" }
function Log-Success { param([string]$Msg) Write-Log "SUCCESS" $Msg "Green" }
function Log-Warn    { param([string]$Msg) Write-Log "WARN"    $Msg "Yellow" }
function Log-Error   { param([string]$Msg) Write-Log "ERROR"   $Msg "Red" }

# ─── 任务检测函数 ───────────────────────────────────────
function Get-NextTask {
    if (-not (Test-Path $TasksFile)) { return $null }
    $lines = Get-Content $TasksFile -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match '^\- \[ \] (T\d+)') {
            return @{
                Line   = $line
                TaskId = $Matches[1]
                Desc   = ($line -replace '^\- \[ \] ', '').Trim()
            }
        }
    }
    return $null
}

function Get-RemainingCount {
    if (-not (Test-Path $TasksFile)) { return 0 }
    $content = Get-Content $TasksFile -Raw -Encoding UTF8
    return ([regex]::Matches($content, '(?m)^\- \[ \] T\d+')).Count
}

function Get-CompletedCount {
    if (-not (Test-Path $TasksFile)) { return 0 }
    $content = Get-Content $TasksFile -Raw -Encoding UTF8
    return ([regex]::Matches($content, '(?m)^\- \[[xX]\] T\d+')).Count
}

# ─── Claude Code Prompt ────────────────────────────────
$ClaudePrompt = @'
You are working on the AI Editorial Pipeline project. Follow these steps precisely:

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

IMPORTANT: Only work on ONE task per session. Do not skip tasks. Do not work on tasks that are already marked [x]. Work in order.
'@

# ─── 主循环 ─────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          AI Editorial Pipeline — 自动开发循环               ║" -ForegroundColor Cyan
Write-Host "║          计划运行: $Runs 轮                                     ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Log-Info "日志文件: $LogFile"
Log-Info "任务文件: $TasksFile"
Log-Info "计划运行 $Runs 轮开发周期"
Write-Host ""

$Completed = 0
$Failed = 0
$Skipped = 0
$StartTime = Get-Date

for ($i = 1; $i -le $Runs; $i++) {
    Write-Host ""
    Write-Host ("━" * 60) -ForegroundColor Cyan
    Log-Info "🔄 轮次 $i / $Runs"
    Write-Host ("━" * 60) -ForegroundColor Cyan

    # 检查剩余任务
    $remaining = Get-RemainingCount
    $done = Get-CompletedCount
    Log-Info "任务进度: 已完成 $done | 剩余 $remaining"

    if ($remaining -eq 0) {
        Log-Success "🎉 所有任务已完成! 无需继续运行。"
        break
    }

    # 获取下一个任务
    $nextTask = Get-NextTask

    if (-not $nextTask) {
        Log-Warn "无法解析下一个任务，跳过本轮"
        $Skipped++
        continue
    }

    $taskId = $nextTask.TaskId
    $taskDesc = $nextTask.Desc

    Log-Info "📋 当前任务: $taskId"
    Log-Info "📝 任务内容: $taskDesc"

    # 调用 Claude Code
    $iterStart = Get-Date
    Log-Info "🤖 正在调用 Claude Code..."

    try {
        $output = & claude --dangerously-skip-permissions `
                           -p $ClaudePrompt `
                           --output-format text `
                           2>&1

        $exitCode = $LASTEXITCODE

        # 记录输出到日志
        $output | ForEach-Object { Add-Content -Path $LogFile -Value $_ -Encoding UTF8 }

        # 也输出到控制台（截取前20行避免刷屏）
        $outputLines = $output -split "`n"
        if ($outputLines.Count -gt 20) {
            $outputLines[0..19] | ForEach-Object { Write-Host $_ }
            Write-Host "... (共 $($outputLines.Count) 行, 完整输出见日志)" -ForegroundColor DarkGray
        } else {
            $output | ForEach-Object { Write-Host $_ }
        }
    }
    catch {
        $exitCode = 1
        Log-Error "Claude 调用异常: $_"
    }

    $iterEnd = Get-Date
    $iterDuration = [math]::Round(($iterEnd - $iterStart).TotalSeconds)

    if ($exitCode -eq 0) {
        # 验证任务是否真的被标记完成
        $newRemaining = Get-RemainingCount
        if ($newRemaining -lt $remaining) {
            Log-Success "✅ $taskId 完成 (耗时 ${iterDuration}s)"
            $Completed++
        }
        else {
            Log-Warn "⚠️  Claude 退出码为0但任务 $taskId 未被标记完成"
            $Failed++
        }
    }
    else {
        Log-Error "❌ $taskId 失败 (退出码: $exitCode, 耗时 ${iterDuration}s)"
        $Failed++
    }

    # 轮次间统计
    Log-Info "本轮统计: 成功=$Completed 失败=$Failed 跳过=$Skipped"

    # 轮次间暂停，避免API速率限制
    if ($i -lt $Runs) {
        Log-Info "⏳ 等待 5 秒后开始下一轮..."
        Start-Sleep -Seconds 5
    }
}

# ─── 最终报告 ───────────────────────────────────────────
$EndTime = Get-Date
$TotalDuration = $EndTime - $StartTime
$TotalMinutes = [math]::Floor($TotalDuration.TotalMinutes)
$TotalSeconds = $TotalDuration.Seconds

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    运行结果报告                              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Log-Info    "总耗时: ${TotalMinutes}分${TotalSeconds}秒"
Log-Info    "计划轮次: $Runs"
Log-Success "成功: $Completed"

if ($Failed -gt 0) { Log-Error "失败: $Failed" } else { Log-Info "失败: 0" }
if ($Skipped -gt 0) { Log-Warn "跳过: $Skipped" } else { Log-Info "跳过: 0" }

Write-Host ""

$finalDone = Get-CompletedCount
$finalRemaining = Get-RemainingCount
Log-Info "最终任务进度: 已完成 $finalDone | 剩余 $finalRemaining"

if ($finalRemaining -eq 0) {
    Log-Success "🎉 所有任务已完成!"
}
else {
    Log-Info "💡 继续运行: .\scripts\run-dev-loop.ps1 -Runs $finalRemaining"
}

Write-Host ""
Log-Info "完整日志: $LogFile"
