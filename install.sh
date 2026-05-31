#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# rpl-magang plugin installer for macOS/Linux
# Remote: curl -fsSL https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.sh | bash
# Local:  ./install.sh
# ============================================================

PLUGIN_NAME="rpl-magang"
PLUGIN_VERSION="1.0.0"
GITHUB_USER="dikdns"
GITHUB_REPO="upi-rpl-laporan-magang"
GITHUB_BRANCH="main"
GITHUB_ARCHIVE="https://github.com/${GITHUB_USER}/${GITHUB_REPO}/archive/refs/heads/${GITHUB_BRANCH}.tar.gz"

CLAUDE_DIR="${HOME}/.claude"
PLUGIN_CACHE="${CLAUDE_DIR}/plugins/cache/${PLUGIN_NAME}/${PLUGIN_NAME}/${PLUGIN_VERSION}"
MARKETPLACE_DIR="${CLAUDE_DIR}/plugins/marketplaces/${PLUGIN_NAME}"
PLUGIN_DATA_DIR="${CLAUDE_DIR}/plugins/data/${PLUGIN_NAME}-${PLUGIN_NAME}"
TOOLS_DIR="${CLAUDE_DIR}/magang-tools"
INSTALLED_PLUGINS="${CLAUDE_DIR}/plugins/installed_plugins.json"
KNOWN_MARKETPLACES="${CLAUDE_DIR}/plugins/known_marketplaces.json"
SETTINGS_JSON="${CLAUDE_DIR}/settings.json"
PLUGIN_KEY="${PLUGIN_NAME}@${PLUGIN_NAME}"
GITHUB_SLUG="${GITHUB_USER}/${GITHUB_REPO}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
log()   { echo -e "${GREEN}[rpl-magang]${NC} $1"; }
warn()  { echo -e "${YELLOW}[rpl-magang]${NC} $1"; }
error() { echo -e "${RED}[rpl-magang]${NC} $1" >&2; }
info()  { echo -e "${BLUE}[rpl-magang]${NC} $1"; }

# ── detect if running from local repo ──────────────────────
SCRIPT_DIR=""
if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != "bash" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

IS_LOCAL=false
if [[ -n "$SCRIPT_DIR" && -f "${SCRIPT_DIR}/.claude-plugin/plugin.json" ]]; then
    IS_LOCAL=true
    log "Local repo detected: ${SCRIPT_DIR}"
fi

# ── check dependencies ──────────────────────────────────────
check_dep() {
    if ! command -v "$1" &>/dev/null; then
        error "Dependency not found: $1"
        error "Install it first, then re-run this script."
        exit 1
    fi
}

check_dep python3
check_dep curl

# ── download or use local source ───────────────────────────
TMP_DIR=""
cleanup() { [[ -n "$TMP_DIR" ]] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

if [[ "$IS_LOCAL" == true ]]; then
    SOURCE_DIR="$SCRIPT_DIR"
else
    log "Downloading rpl-magang from GitHub..."
    TMP_DIR=$(mktemp -d)
    curl -fsSL "$GITHUB_ARCHIVE" -o "${TMP_DIR}/archive.tar.gz"
    tar -xzf "${TMP_DIR}/archive.tar.gz" -C "$TMP_DIR"
    SOURCE_DIR="${TMP_DIR}/${GITHUB_REPO}-${GITHUB_BRANCH}"
fi

# ── install plugin files ────────────────────────────────────
log "Installing plugin files..."
mkdir -p "$PLUGIN_CACHE"
cp -r "${SOURCE_DIR}/." "$PLUGIN_CACHE/"

# ── install marketplace source (required for plugin discovery) ─
log "Registering marketplace..."
rm -rf "$MARKETPLACE_DIR"
mkdir -p "$MARKETPLACE_DIR"
cp -r "${SOURCE_DIR}/." "$MARKETPLACE_DIR/"
rm -rf "${MARKETPLACE_DIR}/.git"
mkdir -p "$PLUGIN_DATA_DIR"

# ── install tools (scripts + assets) ───────────────────────
log "Setting up tools directory..."
mkdir -p "${TOOLS_DIR}/scripts"
mkdir -p "${TOOLS_DIR}/assets"
mkdir -p "${TOOLS_DIR}/templates"
cp "${SOURCE_DIR}/scripts/"*.py "${TOOLS_DIR}/scripts/"
[[ -d "${SOURCE_DIR}/assets" ]]    && cp -r "${SOURCE_DIR}/assets/."    "${TOOLS_DIR}/assets/"
[[ -d "${SOURCE_DIR}/templates" ]] && cp -r "${SOURCE_DIR}/templates/." "${TOOLS_DIR}/templates/"

# ── create python venv ──────────────────────────────────────
log "Setting up Python environment (this may take a moment)..."
python3 -m venv "${TOOLS_DIR}/venv"
"${TOOLS_DIR}/venv/bin/pip" install --quiet --upgrade pip
"${TOOLS_DIR}/venv/bin/pip" install --quiet -r "${SOURCE_DIR}/requirements.txt"
log "Python deps installed."

# ── register plugin across all Claude Code config files ────
# Plugin discovery requires FOUR registrations, not just the cache:
#   1. installed_plugins.json  — the install record
#   2. known_marketplaces.json — resolves the @marketplace source
#   3. settings.json enabledPlugins        — gates whether skills load
#   4. settings.json extraKnownMarketplaces — marketplace allowlist
# Missing any one means skills silently never appear.
log "Registering plugin..."
NOW=$(date -u +%Y-%m-%dT%H:%M:%S.000Z 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%S)
mkdir -p "$(dirname "$INSTALLED_PLUGINS")"

PLUGIN_NAME="$PLUGIN_NAME" PLUGIN_KEY="$PLUGIN_KEY" PLUGIN_VERSION="$PLUGIN_VERSION" \
PLUGIN_CACHE="$PLUGIN_CACHE" MARKETPLACE_DIR="$MARKETPLACE_DIR" GITHUB_SLUG="$GITHUB_SLUG" \
INSTALLED_PLUGINS="$INSTALLED_PLUGINS" KNOWN_MARKETPLACES="$KNOWN_MARKETPLACES" \
SETTINGS_JSON="$SETTINGS_JSON" NOW="$NOW" python3 - <<'PYEOF'
import json, os, pathlib

env = os.environ
name   = env["PLUGIN_NAME"]
key    = env["PLUGIN_KEY"]
ver    = env["PLUGIN_VERSION"]
cache  = env["PLUGIN_CACHE"]
mp_dir = env["MARKETPLACE_DIR"]
slug   = env["GITHUB_SLUG"]
now    = env["NOW"]

def load(path, default):
    p = pathlib.Path(path)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return default

def save(path, data):
    pathlib.Path(path).write_text(json.dumps(data, indent=2))

# 1. installed_plugins.json
ip = load(env["INSTALLED_PLUGINS"], {"version": 2, "plugins": {}})
ip.setdefault("plugins", {})[key] = [{
    "scope": "user", "installPath": cache, "version": ver,
    "installedAt": now, "lastUpdated": now,
}]
save(env["INSTALLED_PLUGINS"], ip)

# 2. known_marketplaces.json
km = load(env["KNOWN_MARKETPLACES"], {})
km[name] = {
    "source": {"source": "github", "repo": slug},
    "installLocation": mp_dir,
    "lastUpdated": now,
}
save(env["KNOWN_MARKETPLACES"], km)

# 3 + 4. settings.json (gate)
st = load(env["SETTINGS_JSON"], {})
st.setdefault("enabledPlugins", {})[key] = True
st.setdefault("extraKnownMarketplaces", {})[name] = {
    "source": {"source": "github", "repo": slug}
}
save(env["SETTINGS_JSON"], st)

print("Registered in installed_plugins, known_marketplaces, and settings.json.")
PYEOF

# ── done ────────────────────────────────────────────────────
echo ""
log "✅ rpl-magang v${PLUGIN_VERSION} installed!"
echo ""
info "Available skills (restart Claude Code to activate):"
info "  /rpl-magang:init     — one-time setup (run this first)"
info "  /rpl-magang:logbook  — generate weekly/biweekly logbook"
info "  /rpl-magang:laporan  — write internship report section by section"
info "  /rpl-magang:pks      — generate cooperation agreement"
echo ""
log "Get started: open Claude Code and run /rpl-magang:init"
