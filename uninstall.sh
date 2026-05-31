#!/usr/bin/env bash
set -euo pipefail

PLUGIN_NAME="rpl-magang"
PLUGIN_VERSION="1.0.0-beta.1"
CLAUDE_DIR="${HOME}/.claude"
PLUGIN_CACHE="${CLAUDE_DIR}/plugins/cache/${PLUGIN_NAME}/${PLUGIN_NAME}/${PLUGIN_VERSION}"
MARKETPLACE_DIR="${CLAUDE_DIR}/plugins/marketplaces/${PLUGIN_NAME}"
PLUGIN_DATA_DIR="${CLAUDE_DIR}/plugins/data/${PLUGIN_NAME}-${PLUGIN_NAME}"
TOOLS_DIR="${CLAUDE_DIR}/magang-tools"
INSTALLED_PLUGINS="${CLAUDE_DIR}/plugins/installed_plugins.json"
KNOWN_MARKETPLACES="${CLAUDE_DIR}/plugins/known_marketplaces.json"
SETTINGS_JSON="${CLAUDE_DIR}/settings.json"
PLUGIN_KEY="${PLUGIN_NAME}@${PLUGIN_NAME}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log()   { echo -e "${GREEN}[rpl-magang]${NC} $1"; }
warn()  { echo -e "${YELLOW}[rpl-magang]${NC} $1"; }

echo ""
warn "This will remove rpl-magang plugin and tools."
warn "Your generated documents and config will NOT be deleted."
echo ""
read -rp "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { log "Aborted."; exit 0; }

[[ -d "$PLUGIN_CACHE" ]]    && { rm -rf "$PLUGIN_CACHE";    log "Removed plugin cache."; }
[[ -d "$MARKETPLACE_DIR" ]] && { rm -rf "$MARKETPLACE_DIR"; log "Removed marketplace."; }
[[ -d "$PLUGIN_DATA_DIR" ]] && { rm -rf "$PLUGIN_DATA_DIR"; log "Removed plugin data."; }
[[ -d "$TOOLS_DIR" ]]       && { rm -rf "$TOOLS_DIR";       log "Removed tools dir."; }

# Unregister from all config files (Python — required by the plugin anyway).
PLUGIN_NAME="$PLUGIN_NAME" PLUGIN_KEY="$PLUGIN_KEY" \
INSTALLED_PLUGINS="$INSTALLED_PLUGINS" KNOWN_MARKETPLACES="$KNOWN_MARKETPLACES" \
SETTINGS_JSON="$SETTINGS_JSON" python3 - <<'PYEOF'
import json, os, pathlib

env = os.environ
name = env["PLUGIN_NAME"]
key  = env["PLUGIN_KEY"]

def edit(path, fn):
    p = pathlib.Path(path)
    if not p.exists():
        return
    try:
        data = json.loads(p.read_text())
    except Exception:
        return
    fn(data)
    p.write_text(json.dumps(data, indent=2))

edit(env["INSTALLED_PLUGINS"], lambda d: d.get("plugins", {}).pop(key, None))
edit(env["KNOWN_MARKETPLACES"], lambda d: d.pop(name, None))

def clean_settings(d):
    d.get("enabledPlugins", {}).pop(key, None)
    d.get("extraKnownMarketplaces", {}).pop(name, None)
edit(env["SETTINGS_JSON"], clean_settings)
print("Unregistered plugin.")
PYEOF

log "✅ rpl-magang uninstalled. Restart Claude Code to apply."
