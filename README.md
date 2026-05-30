# upi-rpl-laporan-magang

Claude Code plugin for RPL students at UPI Cibiru. Generates logbook, laporan magang, and PKS documents based on your pedoman.

## Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.ps1 | iex
```

Restart Claude Code after install.

## Skills

| Skill | What it does |
|-------|-------------|
| `/rpl-magang:init` | One-time setup — parse your pedoman PDF and save config |
| `/rpl-magang:logbook` | Generate weekly/biweekly logbook (Catatan Harian & Kehadiran) |
| `/rpl-magang:laporan` | Write laporan magang section by section, compile to DOCX |
| `/rpl-magang:pks` | Generate PKS (Cooperation Agreement) DOCX |

## Quick start

```
1. /rpl-magang:init              ← run once, point to your pedoman PDF
2. /rpl-magang:logbook           ← generate logbook each week
3. /rpl-magang:laporan bab1      ← write Bab I
4. /rpl-magang:laporan bab2      ← write Bab II
   ...
5. /rpl-magang:laporan compile   ← export full DOCX
6. /rpl-magang:pks               ← generate PKS
```

## Requirements

- Python 3.9+
- Claude Code with superpowers plugin
- `curl` (macOS/Linux) or PowerShell 5+ (Windows)

## Uninstall

```bash
./uninstall.sh
```

## Notes

- UPI logo (`assets/upi-logo.png`) is not bundled. Add it manually before distributing.
- Repo: https://github.com/dikdns/upi-rpl-laporan-magang
- Config stored at `~/.claude/magang-tools/config.json` — re-run `/rpl-magang:init` if your pedoman changes.
