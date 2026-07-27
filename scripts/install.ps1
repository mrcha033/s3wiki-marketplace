[CmdletBinding()]
param(
    [ValidateSet("Auto", "Codex", "Claude", "All")]
    [string]$Client = "Auto",

    [string]$MarketplaceUrl = ""
)

$ErrorActionPreference = "Stop"
$MarketplaceName = "s3wiki-marketplace"
if ([string]::IsNullOrWhiteSpace($MarketplaceUrl)) {
    if (-not [string]::IsNullOrWhiteSpace($env:S3_LAB_MARKETPLACE_URL)) {
        $MarketplaceUrl = $env:S3_LAB_MARKETPLACE_URL
    } else {
        $MarketplaceUrl = "https://github.com/mrcha033/s3wiki-marketplace.git"
    }
}
$PluginId = "s3-lab-workspace@$MarketplaceName"

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Test-Marketplace {
    param([string]$Command)
    $items = & $Command plugin marketplace list --json | ConvertFrom-Json
    if ($Command -eq "codex") {
        return $null -ne ($items.marketplaces | Where-Object { $_.name -eq $MarketplaceName })
    }
    return $null -ne ($items | Where-Object { $_.name -eq $MarketplaceName })
}

function Test-PluginInstalled {
    param([string]$Command)
    $items = & $Command plugin list --json | ConvertFrom-Json
    if ($Command -eq "codex") {
        return $null -ne ($items.installed | Where-Object { $_.pluginId -eq $PluginId })
    }
    return $null -ne ($items | Where-Object { $_.id -eq $PluginId })
}

function Install-CodexPlugin {
    if (-not (Test-Command "codex")) {
        throw "Codex를 찾지 못했습니다."
    }
    if (Test-Marketplace "codex") {
        & codex plugin marketplace upgrade $MarketplaceName
    } else {
        & codex plugin marketplace add $MarketplaceUrl
    }
    if (-not (Test-PluginInstalled "codex")) {
        & codex plugin add $PluginId
    }
    $plugins = & codex plugin list --json | ConvertFrom-Json
    if ($null -eq ($plugins.installed | Where-Object { $_.pluginId -eq $PluginId })) {
        throw "Codex 설치 상태를 확인하지 못했습니다."
    }
    Write-Host "Codex: S3 Lab Workspace 설치 완료"
}

function Install-ClaudePlugin {
    if (-not (Test-Command "claude")) {
        throw "Claude Code를 찾지 못했습니다."
    }
    if (Test-Marketplace "claude") {
        & claude plugin marketplace update $MarketplaceName
    } else {
        & claude plugin marketplace add $MarketplaceUrl
    }
    if (Test-PluginInstalled "claude") {
        & claude plugin update $PluginId
    } else {
        & claude plugin install $PluginId
    }
    $plugins = & claude plugin list --json | ConvertFrom-Json
    if ($null -eq ($plugins | Where-Object { $_.id -eq $PluginId })) {
        throw "Claude Code 설치 상태를 확인하지 못했습니다."
    }
    Write-Host "Claude Code: S3 Lab Workspace 설치 완료"
}

$InstallCodex = $Client -in @("Codex", "All")
$InstallClaude = $Client -in @("Claude", "All")
if ($Client -eq "Auto") {
    $InstallCodex = Test-Command "codex"
    $InstallClaude = Test-Command "claude"
}
if (-not $InstallCodex -and -not $InstallClaude) {
    throw "Codex 또는 Claude Code를 찾지 못했습니다."
}

if ($InstallCodex) { Install-CodexPlugin }
if ($InstallClaude) { Install-ClaudePlugin }

Write-Host "새 작업 또는 세션을 열어 사용하세요."
if ($InstallCodex) {
    Write-Host "Codex 앱: 설치 화면의 Authenticate로 GitHub 로그인을 완료하세요."
    Write-Host "Codex CLI: codex mcp login s3-research-memory"
}
if ($InstallClaude) {
    Write-Host "Claude Code: /mcp에서 S3 Research Memory 로그인을 완료하세요."
}
Write-Host "권한 오류가 나면 명령을 반복하지 말고 연구실 관리자에게 접근 권한을 요청하세요."
