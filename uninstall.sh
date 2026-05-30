#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="rpl-magang"
PLUGIN_VERSION="1.0.0"
CLAUDE_DIR="${HOME}/.claude"
PLUGIN_CACHE="${CLAUDE_DIR}/plugins/cache/local/${PLUGIN_NAME}/${PLUGIN_VERSION}"
TOOLS_DIR="${CLAUDE_DIR}/magang-tools"
INSTALLED_PLUGINS="${CLAUDE_DIR}/plugins/installed_plugins.json"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()   { echo -e "${GREEN}[rpl-magang]${NC} $1"; }
warn()  { echo -e "${YELLOW}[rpl-magang]${NC} $1"; }

echo ""
warn "This will remove rpl-magang plugin and tools."
warn "Your generated documents and config will NOT be deleted."
echo ""
read -rp "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { log "Aborted."; exit 0; }

[[ -d "$PLUGIN_CACHE" ]] && { rm -rf "$PLUGIN_CACHE"; log "Removed plugin cache."; }
[[ -d "$TOOLS_DIR" ]]    && { rm -rf "$TOOLS_DIR";    log "Removed tools dir."; }

if [[ -f "$INSTALLED_PLUGINS" ]] && command -v jq &>/dev/null; then
    jq 'del(.plugins["rpl-magang@local"])' "$INSTALLED_PLUGINS" > "${INSTALLED_PLUGINS}.tmp"
    mv "${INSTALLED_PLUGINS}.tmp" "$INSTALLED_PLUGINS"
    log "Unregistered plugin."
fi

log "✅ rpl-magang uninstalled. Restart Claude Code to apply."
