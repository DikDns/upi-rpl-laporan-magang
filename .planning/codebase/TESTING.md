# Testing Patterns

**Analysis Date:** 2026-06-07

## Test Framework

**Runner:**
- pytest (evidenced by `.pytest_cache/` directory and test file naming)
- Config: no `pytest.ini` or `pyproject.toml` — uses pytest defaults
- Python version: 3.14 (from `__pycache__/init_pedoman.cpython-314.pyc`)

**Assertion Library:**
- pytest built-in `assert` — no custom assertion library

**Run Commands:**
```bash
pytest tests/              # Run all tests
pytest tests/ -v           # Verbose output
pytest tests/ -k "bab"     # Filter by name pattern
```

## Test File Organization

**Location:** Separate `tests/` directory at repo root — NOT co-located with source

**Naming:** `test_<script_name>_<area>.py`
- `tests/test_generate_bab_skills.py` — tests for `scripts/generate_bab_skills.py`
- `tests/test_generate_laporan_toc.py` — tests for TOC/scan functions in `scripts/generate_laporan.py`

**Structure:**
```
tests/
├── test_generate_bab_skills.py   # 81 lines, 7 tests
└── test_generate_laporan_toc.py  # 57 lines, 7 tests
```

## Test Structure

**Suite Organization:**
- No test classes — all top-level functions
- No `setUp`/`tearDown` — each test self-contained
- No pytest fixtures (`@pytest.fixture`) — setup done inline

```python
# tests/test_generate_bab_skills.py

SAMPLE_CONFIG = { ... }  # Module-level fixture dict

def test_bab_map_covers_roman_numerals():
    assert BAB_MAP["babI"] == ("bab1", "BAB I")

def test_render_bab_skill_contains_verbatim_sections():
    bab_data = SAMPLE_CONFIG["document_structure"]["bagian_isi"]["babI"]
    result = render_bab_skill("babI", bab_data, sections_flexible=False)
    assert "name: laporan-bab-1" in result
    assert "1.1" in result
```

**Patterns:**
- Setup: inline dict/tempfile creation inside each test
- Teardown: `tempfile.TemporaryDirectory()` context manager (auto-cleanup)
- Assertion: `assert X in Y` for string content checks, `assert X is True/False` for boolean, `assert len(X) >= N` for structural checks

## Mocking

**Framework:** None — no `unittest.mock`, no `pytest-mock`

**Pattern:** Real filesystem via `tempfile.TemporaryDirectory()` used instead of mocking:
```python
def test_generate_all_writes_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = generate_all(SAMPLE_CONFIG, Path(tmpdir))
        assert len(paths) == 2
        for p in paths:
            assert p.exists()
```

**What to Mock:** Nothing — tests use real file I/O with temp dirs.

**What NOT to Mock:** `python-docx` Document objects — tests create real Document instances and inspect their content.

## Fixtures and Factories

**Test Data:**
```python
# Module-level constant dict used by all tests in the file
SAMPLE_CONFIG = {
    "program": "Rekayasa Perangkat Lunak",
    "document_structure": {
        "bagian_isi": {
            "babI": {
                "title": "Pendahuluan",
                "sections": [
                    {"number": "1.1", "title": "Latar Belakang"},
                    {"number": "1.2", "title": "Manfaat & Tujuan"},
                ]
            },
            ...
        },
        "sections_flexible": True,
    }
}
```

**Helper function pattern** (test_generate_laporan_toc.py):
```python
def _write(tmpdir, name, content):
    p = Path(tmpdir) / name
    p.write_text(content, encoding="utf-8")
    return p
```

**Location:** Fixtures are module-level variables or private functions within the same test file — no shared fixture files.

## Coverage

**Requirements:** None enforced — no coverage config found

**View Coverage:**
```bash
pytest tests/ --cov=scripts --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- All tests are unit-level
- Pure function tests: `render_bab_skill`, `_insert_toc_field`, `scan_has_tables`, `scan_has_images`
- Data map tests: `BAB_MAP` constant values
- File generation tests: `generate_all` output written to tempdir

**Integration Tests:**
- Light integration via real `python-docx` Document creation (no mocking)
- `test_insert_toc_field_*` tests interact with real docx XML structure

**E2E Tests:** Not used — no tests invoke `main()` or the full CLI pipeline

## Common Patterns

**Async Testing:** Not applicable — all code is synchronous

**Filesystem Testing:**
```python
with tempfile.TemporaryDirectory() as tmpdir:
    paths = generate_all(SAMPLE_CONFIG, Path(tmpdir))
    assert len(paths) == 2
    names = [p.parent.name for p in paths]
    assert "laporan-bab-1" in names
```

**String Content Testing:**
```python
result = render_bab_skill("babI", bab_data, sections_flexible=False)
assert "name: laporan-bab-1" in result
assert "1.1" in result
assert "Latar Belakang" in result
```

**Docx XML Testing:**
```python
fld_chars = [el for el in doc.element.body.iter() if el.tag.endswith("}fldChar")]
assert len(fld_chars) >= 2  # begin + end
```

## Path Injection Pattern

All test files manually inject `scripts/` into `sys.path` at the top:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_bab_skills import render_bab_skill, generate_all, BAB_MAP
```

This is the only way tests import from `scripts/` — no package structure, no `__init__.py`.

## Coverage Gaps

**Untested scripts:**
- `scripts/init_pedoman.py` — PDF extraction and config parsing logic has no tests
  - Files: `scripts/init_pedoman.py`
  - Risk: PDF parsing regex (`_parse_bab_outline`, `extract_structure`) could silently produce wrong config
  - Priority: High

- `scripts/generate_logbook.py` — DOCX generation for logbook not tested
  - Files: `scripts/generate_logbook.py`
  - Risk: Formatting regressions undetected
  - Priority: Medium

- `scripts/generate_penilaian.py` — assessment sheet DOCX not tested
  - Files: `scripts/generate_penilaian.py`
  - Risk: Same as logbook
  - Priority: Medium

- `scripts/generate_pks.py` — PKS document generation not tested
  - Files: `scripts/generate_pks.py`
  - Priority: Low

- `scripts/extract_pdf_links.py` — PDF link extraction not tested
  - Files: `scripts/extract_pdf_links.py`
  - Priority: Low

**Untested functions in covered scripts:**
- `compile_sections` in `scripts/generate_laporan.py` (the full pipeline) — only TOC helpers tested
- `render_cover`, `render_lembar_pengesahan` in `scripts/generate_laporan.py`
- `md_to_doc` in `scripts/generate_laporan.py` — markdown-to-docx conversion core

---

*Testing analysis: 2026-06-07*
