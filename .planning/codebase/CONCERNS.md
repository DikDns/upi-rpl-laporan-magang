# Codebase Concerns

**Analysis Date:** 2026-06-07

## Tech Debt

**Version mismatch between plugin.json and install scripts:**
- Issue: `plugin.json` declares `1.0.0-beta.2` but `install.sh` and `install.ps1` both hardcode `PLUGIN_VERSION="1.0.0-beta.1"`. The install scripts embed the version into the plugin cache path, so a user who re-installs gets stale cache paths.
- Files: `.claude-plugin/plugin.json`, `install.sh` (line 5), `install.ps1` (line 4)
- Impact: Plugin discovery may silently use the wrong skill set. Users on the newer manifest version get a mismatched cache directory.
- Fix approach: Single source of truth — read version from `plugin.json` in both install scripts, or use a shared `VERSION` file.

**Hardcoded SECTIONS_ORDER prevents pedoman extensibility:**
- Issue: `generate_laporan.py` has a static `SECTIONS_ORDER` list (cover → bab4 → lampiran). Pedoman editions with 5+ bab or different section names are silently dropped or appended at the end in arbitrary order.
- Files: `scripts/generate_laporan.py` (lines 27–38)
- Impact: Students with a Bab V (some pedoman editions have it) will get it appended out-of-order or not at all.
- Fix approach: Derive section order dynamically from `config["document_structure"]["bagian_isi"]` keys at compile time, keeping cover/front-matter as fixed prefix.

**ROMAN numeral dict capped at VIII:**
- Issue: `init_pedoman.py` defines `ROMAN = {"I":1, ..., "VIII":8}`. Any pedoman with Bab IX or higher (unlikely but possible) fails to parse silently.
- Files: `scripts/init_pedoman.py` (lines 42–43)
- Impact: Sections for Bab IX+ are silently skipped with no error message.
- Fix approach: Use a standard Roman numeral parser or extend the dict to XII.

**`set_fixed_layout` duplicated across two scripts:**
- Issue: Identical `set_fixed_layout` function is copy-pasted in both `generate_laporan.py` and `generate_logbook.py`.
- Files: `scripts/generate_laporan.py` (lines 86–108), `scripts/generate_logbook.py` (lines 50–73)
- Impact: Any bug fix must be applied in both places. Already diverged slightly (logbook version has different comment).
- Fix approach: Extract to a shared `docx_utils.py` helper module in `scripts/`.

**`versioned_path` also duplicated across three scripts:**
- Issue: Identical `versioned_path` function copy-pasted in `generate_laporan.py`, `generate_logbook.py`, and `generate_penilaian.py`.
- Files: all three `scripts/generate_*.py` files
- Impact: Same maintenance problem as above.
- Fix approach: Consolidate into shared `docx_utils.py`.

**`__pycache__` committed to repo:**
- Issue: `scripts/__pycache__/init_pedoman.cpython-314.pyc` is tracked in git.
- Files: `scripts/__pycache__/`
- Impact: Clutters repo, can cause confusion when Python version changes. Byte code is platform/version-specific.
- Fix approach: Add `__pycache__/` and `*.pyc` to `.gitignore` and remove from tracking.

**`.DS_Store` files committed:**
- Issue: `assets/.DS_Store` and root `.DS_Store` are tracked in git.
- Files: `.DS_Store`, `assets/.DS_Store`
- Impact: macOS metadata leaks user filesystem info into the public repo.
- Fix approach: Add `.DS_Store` to `.gitignore` and remove from tracking.

## Known Bugs

**Cover vertical spacing breaks on long names:**
- Symptoms: Cover page content shifts off-page when `nama` or program string is long.
- Files: `scripts/generate_laporan.py` → `render_cover()` (lines 450–503), hardcoded `_gap(doc, 8)` / `_gap(doc, 13)` calls
- Trigger: Student name > ~40 chars, or campus name longer than default.
- Workaround: Documented in `KNOWN_LIMITATIONS.md`. No programmatic mitigation.

**Image forced to 14cm regardless of orientation:**
- Symptoms: Portrait images consume excessive vertical space; small raster images appear pixelated when upscaled to 14cm.
- Files: `scripts/generate_laporan.py` (line 149: `IMG_WIDTH = Cm(14)`)
- Trigger: Any image that is narrower than 14cm or portrait-oriented.
- Workaround: Documented in `KNOWN_LIMITATIONS.md`.

**Figure numbering breaks for non-standard section names:**
- Symptoms: Sections with names not matching `bab\d+` pattern (e.g., `bab-tambahan`) fall back to sequential numbering from `_` key, causing cross-chapter counter collisions.
- Files: `scripts/generate_laporan.py` → `chapter_label_for()` (lines 613–619)
- Trigger: Any section directory name that doesn't contain a digit after "bab".
- Workaround: None documented.

**PKS date fields require manual text entry:**
- Symptoms: `date_tgl_word`, `date_bulan`, `date_tahun_word` are typed as plain strings with no validation or auto-conversion from a date input.
- Files: `scripts/generate_pks.py` (lines 25–41 TOKENS dict)
- Trigger: User types incorrect terbilang (spelled-out date) — no error raised.
- Workaround: Documented in `KNOWN_LIMITATIONS.md`.

**Inline markdown edge case — `apply_inline` splits on nested asterisks:**
- Symptoms: Text like `**word *inner* word**` (bold containing italic) is split incorrectly by the `re.split` pattern, producing malformed runs.
- Files: `scripts/generate_laporan.py` → `apply_inline()` (lines 58–83)
- Trigger: Any markdown that nests `*italic*` inside `**bold**`.
- Workaround: Avoid nesting in source `.md` files.

## Security Considerations

**install.sh modifies `~/.claude/settings.json` without backup:**
- Risk: The installer overwrites the global Claude Code settings file. A malformed JSON in the existing file causes a silent overwrite with partial data.
- Files: `install.sh` (lines 113–166 Python heredoc)
- Current mitigation: The Python snippet uses `try/except` when loading, falling back to an empty dict — meaning an existing valid config survives, but a corrupt JSON results in data loss.
- Recommendations: Backup `settings.json` before writing; validate JSON before saving.

**Installer downloads and executes from GitHub main branch (no integrity check):**
- Risk: `curl -fsSL $GITHUB_ARCHIVE | bash` pattern. The archive URL points to `main` HEAD with no SHA pinning or checksum verification.
- Files: `install.sh` (lines 15, 68–70), `install.ps1` (lines 14, 46–50)
- Current mitigation: None.
- Recommendations: Pin to a tagged release URL; add SHA-256 checksum verification before extraction.

**Python heredoc in install.sh passes env vars into embedded script:**
- Risk: `PLUGIN_CACHE`, `MARKETPLACE_DIR` etc. passed via `os.environ` into an inline Python script. If any value contains newlines or special characters (e.g., a path with spaces on some systems), it could cause unexpected behavior.
- Files: `install.sh` (lines 113–166)
- Current mitigation: None explicit; values are set by the script itself so the attack surface is low in practice.
- Recommendations: Use `--arg` style argument passing or write data to a temp file instead of env vars.

## Performance Bottlenecks

**Full PDF text loaded into memory as a single string:**
- Problem: `init_pedoman.py` concatenates all PDF pages into one string before regex scanning. For large pedoman PDFs (100+ pages), this creates a large in-memory string with O(n) regex scans over it multiple times.
- Files: `scripts/init_pedoman.py` → `main()` (line 275: `full_text = "\n".join(...)`)
- Cause: Simplicity over streaming; acceptable for typical pedoman size (~30–60 pages) but may slow on edge cases.
- Improvement path: Bound the search region (only scan the first N pages for structural data) since structure sections appear near the front of pedoman documents.

**`scan_has_tables` / `scan_has_images` reads every bab file twice at compile time:**
- Problem: Both functions read and scan every bab `.md` file independently. `compile_sections` then reads each file a third time to generate DOCX content.
- Files: `scripts/generate_laporan.py` (lines 298–311, 605–606)
- Cause: Decoupled helper functions with no shared cache.
- Improvement path: Collect the scan results during the single ordered pass, or memoize file reads.

## Fragile Areas

**Skill cache sync in `install.sh` uses glob with version sort:**
- Files: `install.sh` (lines 169–179)
- Why fragile: `ls -d ... | sort -V | tail -1` finds the "latest" version of the plugin cache. If the cache directory structure changes in a future Claude Code release, the glob silently finds nothing and the skill sync step is skipped with no error.
- Safe modification: Add an explicit check and error if `$SKILL_CACHE` is empty after the glob.
- Test coverage: Not tested.

**`_end_section` inserts `w:sectPr` by appending to the last paragraph:**
- Files: `scripts/generate_laporan.py` → `_end_section()` (lines 351–377)
- Why fragile: Appending `sectPr` to an arbitrary "last paragraph" is sensitive to what the previous rendering step produced. If a section ends with a table or image (which don't produce regular paragraphs), the section break is placed incorrectly.
- Safe modification: Always add a sentinel empty paragraph immediately before calling `_end_section`.
- Test coverage: No test for section break behavior.

**PDF heuristic extractor — `bagian_isi` regex bound to "Bagian Akhir" keyword:**
- Files: `scripts/init_pedoman.py` → `extract_structure()` (lines 117–126)
- Why fragile: The regex `r'[Bb]agian\s+Isi.*?(?=[Bb]agian\s+Akhir|\Z)'` requires the PDF text to contain the literal phrase "Bagian Akhir" to terminate the match. Pedoman editions that use a different heading (e.g., "Penutup" or "Bagian Terakhir") fall back to scanning the whole document, potentially pulling in noise.
- Safe modification: Add a fallback stop pattern list rather than a single keyword.
- Test coverage: Tests exist for `generate_bab_skills.py` output but not for `extract_structure` edge cases.

**`laporan` skill step numbering has a gap (Step 2 missing, jumps 3→9):**
- Files: `skills/laporan/SKILL.md` (steps are 1, 3, 3b, 4, 9)
- Why fragile: If any AI executor parses step numbers as sequential dependencies, the missing Step 2 and jump to Step 9 could cause confusion or incorrect execution order.
- Safe modification: Renumber steps sequentially during next skill update.
- Test coverage: Not applicable (natural language instructions).

**`init` skill has Step 8 before Step 7:**
- Files: `skills/init/SKILL.md` (steps are 1–6, then 8, then 7)
- Why fragile: Same issue — out-of-order step numbers. Step 8 (generate bab skills) comes before Step 7 (confirm). This is confusing and may cause a skill runner to show the confirmation before skills are generated.
- Safe modification: Reorder to 1–8 sequentially.
- Test coverage: Not applicable.

## Scaling Limits

**BAB_MAP hard-caps at Bab VI:**
- Current capacity: Generates skills for up to Bab VI (`babI` through `babVI`).
- Limit: Any pedoman with more than 6 bab produces no skill for the extra chapters.
- Scaling path: Make `BAB_MAP` dynamically derived from the config's `bagian_isi` keys, up to a configurable max.
- Files: `scripts/generate_bab_skills.py` (lines 16–23)

## Dependencies at Risk

**`pdfplumber` is a soft optional dependency:**
- Risk: `pdfplumber` import is inside a `try/except` in `extract_pdf_text()`. If the package is missing from the venv (e.g., install step failed silently), the function returns `None` and the init flow falls back to full manual entry — with no clear error message about the missing package.
- Impact: User sees "PDF tidak bisa dibaca otomatis" when the real cause is a missing dependency.
- Migration plan: Check dependency availability explicitly at startup and report which package is missing.
- Files: `scripts/init_pedoman.py` (lines 19–29)

**No version pins beyond minimums:**
- Risk: `requirements.txt` specifies only `>=` lower bounds (`python-docx>=1.1.2`, `pdfplumber>=0.11.0`, `Pillow>=10.0.0`). Future breaking releases of any dependency will break the tool silently after a fresh install.
- Impact: Reproducibility degrades over time.
- Migration plan: Pin to tested version ranges (`>=1.1.2,<2`) or provide a lockfile (`requirements.lock.txt`).
- Files: `requirements.txt`

## Test Coverage Gaps

**No tests for `init_pedoman.py` core extractors:**
- What's not tested: `extract_structure`, `extract_formatting`, `extract_assessment`, `extract_penilaian_penyelia` — the primary PDF parsing logic.
- Files: `scripts/init_pedoman.py` (entire file)
- Risk: Regex heuristics could silently break on a new pedoman edition; no regression protection exists.
- Priority: High — this is the critical path for the entire tool.

**No tests for `generate_laporan.py` DOCX rendering:**
- What's not tested: `render_cover`, `render_lembar_pengesahan`, `md_to_doc`, `compile_sections`, `_end_section`, `_add_page_num_footer`.
- Files: `scripts/generate_laporan.py`
- Risk: Visual regressions (formatting, page breaks, section numbering) are invisible without manual review.
- Priority: High — students submit this output for academic evaluation.

**No tests for `generate_logbook.py` or `generate_penilaian.py`:**
- What's not tested: All DOCX generation logic in both files.
- Files: `scripts/generate_logbook.py`, `scripts/generate_penilaian.py`
- Risk: Breakage only caught by manual run.
- Priority: Medium.

**No tests for `generate_pks.py` token substitution:**
- What's not tested: Template loading, token replacement, output DOCX validity.
- Files: `scripts/generate_pks.py`
- Risk: A token name change or template update goes undetected.
- Priority: Medium.

**Windows installer untested end-to-end:**
- What's not tested: `install.ps1` full flow — venv creation, pip install, JSON registration, skill sync.
- Files: `install.ps1`
- Risk: Windows users get a broken install with no automated safety net.
- Priority: Medium (per `KNOWN_LIMITATIONS.md` acknowledgment).

---

*Concerns audit: 2026-06-07*
