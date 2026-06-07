# Coding Conventions

**Analysis Date:** 2026-06-07

## Naming Patterns

**Files:**
- Snake_case for Python scripts: `generate_laporan.py`, `generate_bab_skills.py`, `init_pedoman.py`
- Test files prefixed with `test_`: `test_generate_bab_skills.py`, `test_generate_laporan_toc.py`
- Skill docs always named `SKILL.md` (uppercase)
- Config always `config.json`, always in `~/.claude/magang-tools/`

**Functions:**
- Public functions: `snake_case` — `render_bab_skill`, `generate_all`, `compile_sections`, `load_config`
- Private helpers: leading underscore — `_sections_block`, `_section_titles_desc`, `_skill_name_dashed`, `_insert_toc_field`, `_end_section`, `_add_page_num_footer`, `_gap`, `_block`
- Nested helpers (closures inside a top-level function): `snake_case` without underscore — `add_heading`, `add_image`, `add_centered_bold`, `add_identity`, `render_uraian`

**Variables:**
- `snake_case` throughout: `bab_key`, `skill_name`, `font_size_pt`, `sections_flexible`
- Module-level constants: `UPPER_SNAKE_CASE` — `BAB_MAP`, `TOOLS_DIR`, `CONFIG_PATH`, `SECTIONS_ORDER`, `SKILL_TEMPLATE`, `ROMAN`
- Long multiline string constants: defined at module level as `UPPER_SNAKE_CASE` — `WRITING_HINTS_TABLE`, `BAB3_FLEXIBILITY_NOTE`, `IMAGE_RULE`, `SKILL_TEMPLATE`

**Types:**
- Python type hints used consistently on all public functions
- Return type annotations: `-> dict`, `-> str`, `-> list`, `-> Path`, `-> list[dict] | None`
- Parameter types annotated: `bab_key: str`, `bab_data: dict`, `sections_flexible: bool`, `sections: list`
- No `TypedDict` or `dataclass` — plain dicts used for all structured data

## Code Style

**Formatting:**
- No formatter config detected (no `.black`, `.flake8`, `pyproject.toml` with format section)
- Consistent 4-space indentation throughout
- Blank lines between top-level functions: 2 blank lines
- Inline comments above logical blocks with `# ── label ───` separator style (init_pedoman.py)

**Linting:**
- No linting config detected

**Shebangs:**
- All runnable scripts start with `#!/usr/bin/env python3`

**Docstrings:**
- Module-level docstrings present on all scripts, describing usage and CLI syntax
- Function-level docstrings only on non-obvious helpers (e.g., `_skill_name_dashed`, `set_fixed_layout`)
- Inner closures: no docstrings

## Import Organization

**Order:**
1. Standard library (`argparse`, `json`, `re`, `sys`, `hashlib`, `tempfile`, `pathlib`)
2. Third-party inside functions only (`from docx import Document`, `import pdfplumber`) — deferred to avoid import errors when optional deps are absent

**Pattern:**
- Standard lib: top-level imports
- Third-party (docx, pdfplumber, PIL): imported inside the function body that uses them, not at module top — prevents `ImportError` on machines missing optional deps

```python
def apply_inline(paragraph, text: str, font_name: str, font_size_pt):
    from docx.shared import Pt
    ...
```

**Path Aliases:** None — all paths constructed via `pathlib.Path`

## Error Handling

**Pattern — CLI scripts output JSON and exit:**
```python
if not config_path.exists():
    print(json.dumps({"error": f"Config not found: {config_path}"}))
    sys.exit(1)
```

**Exit codes are documented and meaningful:**
- `init_pedoman.py`: exit 0=success, 1=file not found, 2=parse failed
- `generate_pks.py`: exit 3=template not found
- Others: exit 1=missing input

**Internal errors swallowed silently in utility functions:**
```python
def extract_pdf_text(pdf_path: str) -> list[dict] | None:
    try:
        ...
    except Exception:
        return None
```

**No custom exception classes** — stdlib exceptions used bare, or silenced.

**Success output:** Always `print(json.dumps({"success": True, "output": str(out)}))` — machine-readable stdout.

## Logging

**Framework:** `print()` only — no logging module

**Pattern:**
- Errors → `print(json.dumps({"error": "..."}))` then `sys.exit(N)`
- Success → `print(json.dumps({"success": True, ...}))`
- No debug logging, no stderr

## Comments

**When to Comment:**
- Block separators using `# ── Section Name ───` at module level (`init_pedoman.py`)
- Inline comments explain non-obvious document formatting decisions (campus conventions, Word XML manipulation)
- Constants that encode domain knowledge get inline comments

**Pattern:**
```python
# Campus heading convention (from reference proposal), NOT Word's blue
# built-in heading styles: black, bold, document font, explicit sizes.
#   H1 (BAB)  -> chapter size, CENTER
```

## Function Design

**Size:** Functions kept focused. Large orchestration functions (`compile_sections`, `md_to_doc`, `generate`) use nested closures to group related behavior without splitting into separate top-level functions.

**Parameters:** Config and Path objects passed explicitly — no globals read inside functions (module-level constants `TOOLS_DIR`/`CONFIG_PATH` used only in `main()`).

**Return Values:**
- Generator/collector functions return `list` of `Path` objects
- Single-output functions return `Path`
- Pure text renderers return `str`
- `main()` functions return nothing — side effects + `sys.exit`

## Module Design

**Exports:** No `__all__` defined — modules expose everything; tests import named symbols directly.

**Entry point pattern:**
```python
if __name__ == "__main__":
    main()
```
All scripts follow this pattern.

**Barrel Files:** None — each script is standalone, tests add parent dir to `sys.path` manually.

---

*Convention analysis: 2026-06-07*
