<!-- refreshed: 2026-06-07 -->
# Architecture

**Analysis Date:** 2026-06-07

## System Overview

```text
┌──────────────────────────────────────────────────────────────┐
│                    Claude Code Plugin                        │
│               (rpl-magang — /rpl-magang:*)                   │
├──────────┬───────────┬──────────┬────────────┬──────────────┤
│  init    │  laporan  │ laporan- │  logbook   │  penilaian-  │
│          │           │ compile  │            │  penyelia/   │
│          │           │          │            │    pks       │
│`skills/  │`skills/   │`skills/  │`skills/    │`skills/      │
│init/`    │laporan/`  │laporan-  │logbook/`   │penilaian-    │
│          │           │compile/` │            │penyelia/`    │
│          │           │          │            │`skills/pks/` │
└────┬─────┴─────┬─────┴────┬─────┴─────┬──────┴──────┬───────┘
     │           │          │           │             │
     ▼           ▼          ▼           ▼             ▼
┌──────────────────────────────────────────────────────────────┐
│               Python Script Layer                            │
│         `scripts/` (executed via venv python)                │
│  init_pedoman.py  generate_laporan.py  generate_logbook.py   │
│  generate_bab_skills.py  generate_penilaian.py               │
│  generate_pks.py  extract_pdf_links.py                       │
└────────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────┐
│              Persistent State & Assets                       │
│  ~/.claude/magang-tools/config.json   (runtime config)       │
│  ~/.claude/magang-tools/generated-skills/   (dynamic skills) │
│  ~/.claude/magang-tools/assets/upi-logo.png                  │
│  templates/pks_template.docx   (PKS base template)           │
└──────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| init skill | One-time setup: parse pedoman PDF, build config, generate per-bab skills | `skills/init/SKILL.md` |
| laporan skill | Guide writing front-matter sections (cover, lembar-pengesahan, kata-pengantar) | `skills/laporan/SKILL.md` |
| laporan-compile skill | Compile all .md section drafts into a single DOCX | `skills/laporan-compile/SKILL.md` |
| logbook skill | Generate weekly catatan harian logbook, supports single/batch/import modes | `skills/logbook/SKILL.md` |
| penilaian-penyelia skill | Generate official Lembar Penilaian Penyelia DOCX | `skills/penilaian-penyelia/SKILL.md` |
| pks skill | Fill PKS DOCX template with partner placeholders | `skills/pks/SKILL.md` |
| init_pedoman.py | Parse pedoman PDF via pdfplumber, extract formatting/structure config, write config.json | `scripts/init_pedoman.py` |
| generate_laporan.py | Render .md section files into a single A4 DOCX (cover, bab, images, TOC) | `scripts/generate_laporan.py` |
| generate_logbook.py | Render logbook data JSON into DOCX (catatan harian per-week tables) | `scripts/generate_logbook.py` |
| generate_bab_skills.py | Dynamically generate per-bab SKILL.md files from config.json structure | `scripts/generate_bab_skills.py` |
| generate_penilaian.py | Render penilaian penyelia DOCX (indicator table, identity block, signature) | `scripts/generate_penilaian.py` |
| generate_pks.py | Fill PKS DOCX template tokens with partner data | `scripts/generate_pks.py` |
| extract_pdf_links.py | Extract hyperlinks from PDF files (used by logbook import mode) | `scripts/extract_pdf_links.py` |
| config.json | Central runtime config: pedoman formatting, bab structure, student identity, file naming | `~/.claude/magang-tools/config.json` |

## Pattern Overview

**Overall:** Claude Code Plugin with AI-guided document generation

**Key Characteristics:**
- Skills are markdown instruction files (SKILL.md) that direct Claude's behavior; no runtime code executes in skills
- Python scripts are pure DOCX generators invoked via subprocess/shell calls from within Claude-guided sessions
- All skills share state through a single JSON config at `~/.claude/magang-tools/config.json`
- Per-bab skills are dynamically generated at init time by `generate_bab_skills.py` from the user's pedoman structure
- All document generation outputs are versioned (`_v2`, `_v3`) to prevent accidental overwrites

## Layers

**Skill Layer (AI instruction layer):**
- Purpose: Prompt Claude on what to ask, when to call scripts, and how to format output
- Location: `skills/`
- Contains: SKILL.md files with YAML frontmatter + XML-tagged instruction blocks
- Depends on: Python scripts in `~/.claude/magang-tools/scripts/`
- Used by: Claude Code plugin system (`/rpl-magang:*` slash commands)

**Script Layer (Python DOCX generation):**
- Purpose: Actually produce .md drafts, .docx output files, and config JSON
- Location: `scripts/` (installed to `~/.claude/magang-tools/scripts/`)
- Contains: Python 3 scripts using python-docx, pdfplumber, Pillow
- Depends on: `~/.claude/magang-tools/venv/`, `config.json`, input .md draft files
- Used by: Skills (via bash subprocess calls)

**Config Layer (persistent state):**
- Purpose: Share pedoman-extracted configuration across all skills and runs
- Location: `~/.claude/magang-tools/config.json`
- Contains: formatting (font, margin, spacing), bab structure, student identity, file naming conventions, penilaian indicators
- Depends on: `init_pedoman.py` (writes), `init_pedoman.py` fallback (manual input)
- Used by: All skills and all scripts

**Template Layer (static assets):**
- Purpose: Base DOCX templates for documents requiring fixed legal/institutional text
- Location: `templates/`, `assets/`
- Contains: `templates/pks_template.docx` (PKS agreement), `assets/upi-logo.png`
- Depends on: Nothing (static)
- Used by: `generate_pks.py` (fills partner tokens), `generate_laporan.py` (logo embed)

**Generated Skills Layer (dynamic):**
- Purpose: Per-bab SKILL.md files customized to the student's specific pedoman structure
- Location: `~/.claude/magang-tools/generated-skills/laporan-bab-{1..4}/`
- Synced to: `~/.claude/plugins/cache/rpl-magang/rpl-magang/*/skills/`
- Contains: SKILL.md files generated by `generate_bab_skills.py` from config.json bab structure
- Depends on: `config.json` bab structure, `generate_bab_skills.py`
- Used by: Claude Code as `/rpl-magang:laporan-bab-1` through `/rpl-magang:laporan-bab-4`

## Data Flow

### Primary Laporan Authoring Flow

1. User runs `/rpl-magang:init` → `init/SKILL.md` guides Claude
2. Claude calls `init_pedoman.py --pdf [path]` → extracts config → writes `~/.claude/magang-tools/config.json`
3. Claude calls `generate_bab_skills.py --config ... --output-dir ...` → creates per-bab SKILL.md files
4. Skills are synced to plugin cache → Claude Code registers `/rpl-magang:laporan-bab-*`
5. User runs `/rpl-magang:laporan [section]` → Claude writes `.md` draft to `./laporan-draft/`
6. User runs `/rpl-magang:laporan-bab-1` etc. → Claude writes bab `.md` drafts
7. User runs `/rpl-magang:laporan-compile` → Claude calls `generate_laporan.py --sections-dir ./laporan-draft --output Laporan.docx`
8. `generate_laporan.py` reads config, merges section .md files, renders DOCX with UPI formatting

### Logbook Flow

1. User runs `/rpl-magang:logbook [--week N|--batch|--import /path]`
2. Claude reads config for student identity (reuses, never re-asks if present)
3. Claude collects daily activities, expands them to formal Bahasa Indonesia prose
4. Claude writes `.md` draft to output dir
5. Claude writes JSON to `/tmp/logbook_data_[week].json`
6. Claude calls `generate_logbook.py --data /tmp/... --output ...`
7. Script renders DOCX with per-week table layout + signature blocks

### PKS Flow

1. User runs `/rpl-magang:pks`
2. Claude collects partner (PIHAK KEDUA) fields
3. Claude writes JSON to `/tmp/pks_data_[timestamp].json`
4. Claude calls `generate_pks.py --data /tmp/... --output PKS_[Company].docx`
5. Script fills tokenized placeholders in `templates/pks_template.docx`, outputs versioned file

**State Management:**
- Shared state lives entirely in `~/.claude/magang-tools/config.json` — written by `init` skill, read by all others
- `student_identity` within config is lazily populated: any skill that collects identity writes it back for reuse
- No in-process state; all state persists across sessions via config.json

## Key Abstractions

**SKILL.md:**
- Purpose: Declarative AI behavior spec — tells Claude what to ask, what bash commands to run, and in what order
- Examples: `skills/init/SKILL.md`, `skills/laporan/SKILL.md`, `skills/logbook/SKILL.md`
- Pattern: YAML frontmatter (name, description, allowed-tools) + XML-tagged `<objective>`, `<constants>`, `<steps>` blocks

**config.json:**
- Purpose: Runtime contract between all skills and scripts; schema defined by `init_pedoman.py`
- Key fields: `formatting` (font/margin/spacing), `document_structure` (bagian_awal/bab structure), `student_identity`, `file_naming`, `penilaian_penyelia`
- Pattern: Read by every script on startup; partially written by logbook/pks skills when identity is collected

**DOCX Generator Script:**
- Purpose: Python function that accepts a data dict + output path, produces a DOCX file
- Examples: `scripts/generate_laporan.py`, `scripts/generate_logbook.py`, `scripts/generate_penilaian.py`
- Pattern: Reads config.json → builds python-docx Document → applies UPI formatting → calls `versioned_path()` → outputs JSON result to stdout

**Versioned Output:**
- Purpose: Prevent accidental file overwrites on re-runs
- Implementation: `versioned_path()` in `scripts/generate_laporan.py` — appends `_v2`, `_v3`, etc.
- Used by all generator scripts

## Entry Points

**`/rpl-magang:init`:**
- Location: `skills/init/SKILL.md`
- Triggers: User command; one-time setup
- Responsibilities: Parse pedoman PDF, build config.json, generate per-bab skills

**`/rpl-magang:laporan`:**
- Location: `skills/laporan/SKILL.md`
- Triggers: User command with section arg (cover/lembar-pengesahan/kata-pengantar)
- Responsibilities: Guide section writing, write .md draft

**`/rpl-magang:laporan-compile`:**
- Location: `skills/laporan-compile/SKILL.md`
- Triggers: User command after all sections drafted
- Responsibilities: Call `generate_laporan.py`, confirm output

**`/rpl-magang:laporan-bab-{1..4}` (generated):**
- Location: `~/.claude/magang-tools/generated-skills/laporan-bab-N/SKILL.md`
- Triggers: User command per bab
- Responsibilities: Guide bab writing with sub-section structure from config

**`/rpl-magang:logbook`:**
- Location: `skills/logbook/SKILL.md`
- Triggers: User command (single/batch/import modes)
- Responsibilities: Collect activities, write draft, call `generate_logbook.py`

**`/rpl-magang:pks`:**
- Location: `skills/pks/SKILL.md`
- Triggers: User command
- Responsibilities: Collect partner info, call `generate_pks.py`

**`/rpl-magang:penilaian-penyelia`:**
- Location: `skills/penilaian-penyelia/SKILL.md`
- Triggers: User command
- Responsibilities: Collect identity/scores, call `generate_penilaian.py`

## Architectural Constraints

- **Python venv:** All scripts must be called via `~/.claude/magang-tools/venv/bin/python` — system Python lacks required packages
- **Config dependency:** Every skill gates on `config.json` existence; init must run first. Hard stop if missing.
- **Generated skill sync:** After `generate_bab_skills.py` runs, skills must be copied to plugin cache path (`~/.claude/plugins/cache/rpl-magang/rpl-magang/*/skills/`) and Claude Code restarted to activate them
- **Global state:** `~/.claude/magang-tools/config.json` is a single shared mutable file. Concurrent skill runs would cause conflicts (not a practical concern for a single-user CLI tool)
- **Temp files:** Scripts use `/tmp/` for data JSON handoff; skills are responsible for cleanup after script call
- **Script output protocol:** Scripts output a JSON object to stdout — skills parse this to get file paths and handle errors. Non-zero exit codes = error condition.

## Anti-Patterns

### Calling system python instead of venv python

**What happens:** Running `python3 script.py` instead of `~/.claude/magang-tools/venv/bin/python script.py`
**Why it's wrong:** System Python lacks python-docx, pdfplumber, Pillow — script will fail with ImportError
**Do this instead:** Always use the constant `PYTHON = ~/.claude/magang-tools/venv/bin/python` defined in each skill's `<constants>` block

### Writing prose into key:value-only .md files

**What happens:** Adding headings, paragraphs, or extra fields to `cover.md` or `lembar-pengesahan.md`
**Why it's wrong:** `generate_laporan.py` parses these as key:value data and renders the layout itself; extra content corrupts the cover/pengesahan page layout
**Do this instead:** Write ONLY the specified key:value lines as documented in `skills/laporan/SKILL.md` Steps 3 and 3b

### Skipping init before other skills

**What happens:** Running laporan/logbook/pks/penilaian skills without config.json present
**Why it's wrong:** All skills and scripts read config.json at startup; missing config causes immediate hard stop
**Do this instead:** Always run `/rpl-magang:init` first; each skill checks for config and shows a clear error if missing

## Error Handling

**Strategy:** Fail-fast with clear user messaging; no silent failures

**Patterns:**
- Config missing → immediate stop with "Jalankan /rpl-magang:init dulu."
- PDF parse failure (exit code 2) → fallback to manual config collection (init skill Step 3b)
- Missing image file → placeholder text `[Gambar tidak ditemukan: ...]` rendered inline, caption numbering continues
- Output file exists → auto-versioned path (`_v2`, `_v3`) returned to user
- Script error → parse JSON output, display error message to user, stop

## Cross-Cutting Concerns

**Language:** All AI-generated prose output is always formal Bahasa Indonesia academic style regardless of user input language. Technical/foreign terms in italic.
**RPL Emphasis:** Every bab (I–IV) surfaces a reminder to highlight Software Engineering angle — defined in `skills/laporan/SKILL.md` `<rpl-emphasis-rule>`.
**Student Identity Reuse:** `student_identity` in config.json is read by laporan, logbook, pks, penilaian-penyelia skills — collected once, reused with confirmation only.
**Image Auto-numbering:** `generate_laporan.py` auto-numbers images as "Gambar {bab}.{seq}" scoped per chapter label, centered, 14cm wide.

---

*Architecture analysis: 2026-06-07*
