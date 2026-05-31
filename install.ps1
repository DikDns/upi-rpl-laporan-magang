# ============================================================
# rpl-magang plugin installer for Windows (PowerShell)
# Remote: irm https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.ps1 | iex
# Local:  .\install.ps1
# ============================================================

$ErrorActionPreference = "Stop"

$PLUGIN_NAME    = "rpl-magang"
$PLUGIN_VERSION = "1.0.0"
$GITHUB_USER    = "dikdns"
$GITHUB_REPO    = "upi-rpl-laporan-magang"
$GITHUB_BRANCH  = "main"
$GITHUB_ARCHIVE = "https://github.com/$GITHUB_USER/$GITHUB_REPO/archive/refs/heads/$GITHUB_BRANCH.zip"

$ClaudeDir      = Join-Path $env:USERPROFILE ".claude"
$PluginCache    = Join-Path $ClaudeDir "plugins\cache\$PLUGIN_NAME\$PLUGIN_NAME\$PLUGIN_VERSION"
$ToolsDir       = Join-Path $ClaudeDir "magang-tools"
$PluginsJson    = Join-Path $ClaudeDir "plugins\installed_plugins.json"

function Log   { param($msg) Write-Host "[rpl-magang] $msg" -ForegroundColor Green }
function Warn  { param($msg) Write-Host "[rpl-magang] $msg" -ForegroundColor Yellow }
function Error { param($msg) Write-Host "[rpl-magang] $msg" -ForegroundColor Red }

# ── check Python ─────────────────────────────────────────────
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Error "Python not found. Install Python 3 from https://python.org and re-run."
    exit 1
}

# ── detect local repo ─────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$IsLocal   = Test-Path (Join-Path $ScriptDir ".claude-plugin\plugin.json")

if ($IsLocal) {
    Log "Local repo detected: $ScriptDir"
    $SourceDir = $ScriptDir
} else {
    Log "Downloading rpl-magang from GitHub..."
    $TmpDir = [System.IO.Path]::GetTempPath() + [System.Guid]::NewGuid().ToString()
    New-Item -ItemType Directory -Path $TmpDir | Out-Null
    $ZipPath = Join-Path $TmpDir "archive.zip"
    Invoke-WebRequest -Uri $GITHUB_ARCHIVE -OutFile $ZipPath
    Expand-Archive -Path $ZipPath -DestinationPath $TmpDir
    $SourceDir = Join-Path $TmpDir "$GITHUB_REPO-$GITHUB_BRANCH"
}

# ── install plugin files ──────────────────────────────────────
Log "Installing plugin files..."
New-Item -ItemType Directory -Force -Path $PluginCache | Out-Null
Copy-Item -Path "$SourceDir\*" -Destination $PluginCache -Recurse -Force

# ── install tools ─────────────────────────────────────────────
Log "Setting up tools directory..."
New-Item -ItemType Directory -Force -Path "$ToolsDir\scripts"   | Out-Null
New-Item -ItemType Directory -Force -Path "$ToolsDir\assets"    | Out-Null
New-Item -ItemType Directory -Force -Path "$ToolsDir\templates" | Out-Null
Copy-Item -Path "$SourceDir\scripts\*.py" -Destination "$ToolsDir\scripts\" -Force
if (Test-Path "$SourceDir\assets")    { Copy-Item "$SourceDir\assets\*"    "$ToolsDir\assets\"    -Recurse -Force }
if (Test-Path "$SourceDir\templates") { Copy-Item "$SourceDir\templates\*" "$ToolsDir\templates\" -Recurse -Force }

# ── venv ──────────────────────────────────────────────────────
Log "Setting up Python environment..."
python -m venv "$ToolsDir\venv"
& "$ToolsDir\venv\Scripts\pip.exe" install --quiet --upgrade pip
& "$ToolsDir\venv\Scripts\pip.exe" install --quiet -r "$SourceDir\requirements.txt"
Log "Python deps installed."

# ── register plugin ───────────────────────────────────────────
Log "Registering plugin..."
$Now       = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
$PluginKey = "$PLUGIN_NAME@$PLUGIN_NAME"
$Entry     = @{
    scope       = "user"
    installPath = $PluginCache
    version     = $PLUGIN_VERSION
    installedAt = $Now
    lastUpdated = $Now
}

New-Item -ItemType Directory -Force -Path (Split-Path $PluginsJson) | Out-Null

if (Test-Path $PluginsJson) {
    $data = Get-Content $PluginsJson -Raw | ConvertFrom-Json
} else {
    $data = [PSCustomObject]@{ version = 2; plugins = [PSCustomObject]@{} }
}

$data.plugins | Add-Member -NotePropertyName $PluginKey -NotePropertyValue @($Entry) -Force
$data | ConvertTo-Json -Depth 10 | Set-Content $PluginsJson

# ── done ──────────────────────────────────────────────────────
Write-Host ""
Log "✅ rpl-magang v$PLUGIN_VERSION installed!"
Write-Host ""
Write-Host "[rpl-magang] Available skills (restart Claude Code to activate):" -ForegroundColor Cyan
Write-Host "  /rpl-magang:init     — one-time setup (run this first)" -ForegroundColor Cyan
Write-Host "  /rpl-magang:logbook  — generate weekly/biweekly logbook" -ForegroundColor Cyan
Write-Host "  /rpl-magang:laporan  — write internship report section by section" -ForegroundColor Cyan
Write-Host "  /rpl-magang:pks      — generate cooperation agreement" -ForegroundColor Cyan
Write-Host ""
Log "Get started: open Claude Code and run /rpl-magang:init"
