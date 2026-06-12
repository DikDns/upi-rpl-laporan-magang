# ============================================================
# rpl-magang plugin installer for Windows (PowerShell)
# Remote: irm https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.ps1 | iex
# Local:  .\install.ps1
# ============================================================

$ErrorActionPreference = "Stop"

$PLUGIN_NAME    = "rpl-magang"
$PLUGIN_VERSION = "1.0.0-rc.1"
$GITHUB_USER    = "dikdns"
$GITHUB_REPO    = "upi-rpl-laporan-magang"
$GITHUB_BRANCH  = "main"
$GITHUB_ARCHIVE = "https://github.com/$GITHUB_USER/$GITHUB_REPO/archive/refs/heads/$GITHUB_BRANCH.zip"

$ClaudeDir         = Join-Path $env:USERPROFILE ".claude"
$PluginCache       = Join-Path $ClaudeDir "plugins\cache\$PLUGIN_NAME\$PLUGIN_NAME\$PLUGIN_VERSION"
$MarketplaceDir    = Join-Path $ClaudeDir "plugins\marketplaces\$PLUGIN_NAME"
$PluginDataDir     = Join-Path $ClaudeDir "plugins\data\$PLUGIN_NAME-$PLUGIN_NAME"
$ToolsDir          = Join-Path $ClaudeDir "magang-tools"
$PluginsJson       = Join-Path $ClaudeDir "plugins\installed_plugins.json"
$KnownMarketplaces = Join-Path $ClaudeDir "plugins\known_marketplaces.json"
$SettingsJson      = Join-Path $ClaudeDir "settings.json"
$PluginKey         = "$PLUGIN_NAME@$PLUGIN_NAME"
$GithubSlug        = "$GITHUB_USER/$GITHUB_REPO"

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

# ── install marketplace source (required for plugin discovery) ─
Log "Registering marketplace..."
if (Test-Path $MarketplaceDir) { Remove-Item -Recurse -Force $MarketplaceDir }
New-Item -ItemType Directory -Force -Path $MarketplaceDir | Out-Null
Copy-Item -Path "$SourceDir\*" -Destination $MarketplaceDir -Recurse -Force
$mpGit = Join-Path $MarketplaceDir ".git"
if (Test-Path $mpGit) { Remove-Item -Recurse -Force $mpGit }
New-Item -ItemType Directory -Force -Path $PluginDataDir | Out-Null

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

# ── register plugin across all Claude Code config files ────────
# Plugin discovery requires FOUR registrations, not just the cache:
#   1. installed_plugins.json  — the install record
#   2. known_marketplaces.json — resolves the @marketplace source
#   3. settings.json enabledPlugins        — gates whether skills load
#   4. settings.json extraKnownMarketplaces — marketplace allowlist
# Missing any one means skills silently never appear.
# Done in Python (required anyway) to keep one source of truth with install.sh.
Log "Registering plugin..."
$Now = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
New-Item -ItemType Directory -Force -Path (Split-Path $PluginsJson) | Out-Null

$env:PLUGIN_NAME        = $PLUGIN_NAME
$env:PLUGIN_KEY         = $PluginKey
$env:PLUGIN_VERSION     = $PLUGIN_VERSION
$env:PLUGIN_CACHE       = $PluginCache
$env:MARKETPLACE_DIR    = $MarketplaceDir
$env:GITHUB_SLUG        = $GithubSlug
$env:INSTALLED_PLUGINS  = $PluginsJson
$env:KNOWN_MARKETPLACES = $KnownMarketplaces
$env:SETTINGS_JSON      = $SettingsJson
$env:NOW                = $Now

$pyReg = @'
import json, os, pathlib
env = os.environ
name, key, ver = env["PLUGIN_NAME"], env["PLUGIN_KEY"], env["PLUGIN_VERSION"]
cache, mp_dir, slug, now = env["PLUGIN_CACHE"], env["MARKETPLACE_DIR"], env["GITHUB_SLUG"], env["NOW"]

def load(path, default):
    p = pathlib.Path(path)
    if p.exists():
        try: return json.loads(p.read_text())
        except Exception: pass
    return default

def save(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2))

ip = load(env["INSTALLED_PLUGINS"], {"version": 2, "plugins": {}})
ip.setdefault("plugins", {})[key] = [{
    "scope": "user", "installPath": cache, "version": ver,
    "installedAt": now, "lastUpdated": now}]
save(env["INSTALLED_PLUGINS"], ip)

km = load(env["KNOWN_MARKETPLACES"], {})
km[name] = {"source": {"source": "github", "repo": slug},
            "installLocation": mp_dir, "lastUpdated": now}
save(env["KNOWN_MARKETPLACES"], km)

st = load(env["SETTINGS_JSON"], {})
st.setdefault("enabledPlugins", {})[key] = True
st.setdefault("extraKnownMarketplaces", {})[name] = {"source": {"source": "github", "repo": slug}}
save(env["SETTINGS_JSON"], st)
print("Registered in installed_plugins, known_marketplaces, and settings.json.")
'@
$pyReg | python -

# ── done ──────────────────────────────────────────────────────
Write-Host ""
Log "✅ rpl-magang v$PLUGIN_VERSION installed!"
Warn "Release candidate — selalu cek hasil DOCX manual. Lapor bug di GitHub issues."
Write-Host ""
Write-Host "[rpl-magang] Available skills (restart Claude Code to activate):" -ForegroundColor Cyan
Write-Host "  /rpl-magang:init     — one-time setup (run this first)" -ForegroundColor Cyan
Write-Host "  /rpl-magang:logbook  — generate weekly/biweekly logbook" -ForegroundColor Cyan
Write-Host "  /rpl-magang:laporan  — write internship report section by section" -ForegroundColor Cyan
Write-Host "  /rpl-magang:pks      — generate cooperation agreement" -ForegroundColor Cyan
Write-Host ""
Log "Get started: open Claude Code and run /rpl-magang:init"
