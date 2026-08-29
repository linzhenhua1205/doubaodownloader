# Agent Skills 批量下载脚本
# 用法: .\download-skills.ps1 [-TargetDir <path>] [-SkipExisting]
param(
    [string]$TargetDir = "D:\123\cowkb\tmp\skills",
    [switch]$SkipExisting = $true
)

$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

# ──── 鱼皮博客精选 Skills 仓库列表 ────
$repos = @(
    # 官方 Skills
    @{url="https://github.com/anthropics/skills.git";            name="anthropics-skills"},
    @{url="https://github.com/openai/skills.git";                name="openai-skills"},
    @{url="https://github.com/vercel-labs/agent-skills.git";     name="vercel-agent-skills"},
    @{url="https://github.com/expo/skills.git";                  name="expo-skills"},
    @{url="https://github.com/kepano/obsidian-skills.git";       name="obsidian-skills"},
    @{url="https://github.com/stripe/ai.git";                    name="stripe-ai-skills"},
    @{url="https://github.com/trailofbits/skills.git";           name="trailofbits-skills"},
    @{url="https://github.com/vuejs-ai/skills.git";              name="vuejs-skills"},
    @{url="https://github.com/supabase/agent-skills.git";        name="supabase-agent-skills"},
    @{url="https://github.com/remotion-dev/skills.git";          name="remotion-skills"},
    @{url="https://github.com/heygen-com/skills.git";            name="heygen-skills"},

    # 资源合集
    @{url="https://github.com/ComposioHQ/awesome-claude-skills.git"; name="awesome-claude-skills"},
    @{url="https://github.com/affaan-m/everything-claude-code.git";  name="everything-claude-code"},

    # 工具与管理
    @{url="https://github.com/yusufkaraaslan/Skill_Seekers.git";     name="skill-seekers"},
    @{url="https://github.com/vercel-labs/agent-browser.git";        name="agent-browser"},

    # 项目开发
    @{url="https://github.com/obra/superpowers.git";                 name="superpowers"},
    @{url="https://github.com/OthmanAdi/planning-with-files.git";    name="planning-with-files"},
    @{url="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git"; name="ui-ux-pro-max"},
    @{url="https://github.com/browser-use/browser-use.git";          name="browser-use"},

    # 内容创作
    @{url="https://github.com/JimLiu/baoyu-skills.git";              name="baoyu-skills"},
    @{url="https://github.com/blader/humanizer.git";                 name="humanizer"},
    @{url="https://github.com/marketingskills/marketingskills.git";  name="marketingskills"},
    @{url="https://github.com/squirrelscan/skills.git";              name="squirrelscan-skills"},

    # 额外补充 — Skills 发现与管理
    @{url="https://github.com/vercel-labs/skills.git";               name="vercel-skills"},
    @{url="https://github.com/Kamalnrf/claude-plugins.git";           name="claude-plugins"},

    # 额外补充 — 设计与开发
    @{url="https://github.com/nicobao/agent-skills.git";              name="nicobao-agent-skills"},
    @{url="https://github.com/anthropics/claude-code.git";            name="claude-code"}
)

$total = $repos.Count
$success = 0
$failed = 0
$failedList = @()

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agent Skills 批量下载" -ForegroundColor Cyan
Write-Host "  目标目录: $TargetDir" -ForegroundColor Cyan
Write-Host "  仓库总数: $total" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$index = 0
foreach ($repo in $repos) {
    $index++
    $targetPath = Join-Path $TargetDir $repo.name

    if ($SkipExisting -and (Test-Path $targetPath)) {
        Write-Host "[$index/$total] SKIP  $($repo.name) (已存在)" -ForegroundColor Yellow
        $success++
        continue
    }

    Write-Host "[$index/$total] CLONE $($repo.name) ..." -ForegroundColor Green -NoNewline
    try {
        git clone --depth 1 $repo.url $targetPath 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host " OK" -ForegroundColor Green
            $success++
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            $failed++
            $failedList += $repo.url
        }
    } catch {
        Write-Host " FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $failed++
        $failedList += $repo.url
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成: $success / $total 成功" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
if ($failed -gt 0) {
    Write-Host "  失败列表:" -ForegroundColor Red
    $failedList | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
}
Write-Host "========================================" -ForegroundColor Cyan