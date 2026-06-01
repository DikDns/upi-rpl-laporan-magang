# Penilaian Penyelia Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `/rpl-magang:penilaian-penyelia` skill that generates the official pedoman-v6 "Lembar Penilaian Penyelia" DOCX (blank by default, optional prefilled scores), with indicators extracted at init into config.

**Architecture:** A new standalone DOCX generator script (`generate_penilaian.py`) built from scratch with python-docx, mirroring `generate_logbook.py`'s helpers and config-driven formatting. `init_pedoman.py` gains a `penilaian_penyelia` extractor with a bundled pedoman-v6 fallback. A new `SKILL.md` orchestrates: read config → collect identity (reusing `student_identity`) → optional scores → run generator. README/CHANGELOG updated. Deploys via the existing `install.sh` glob.

**Tech Stack:** Python 3 + python-docx + pdfplumber (venv at `~/.claude/magang-tools/venv`), Claude Code skills (Markdown SKILL.md).

---

## Repo conventions (read before starting)

- No pytest / no test suite exists. Scripts are standalone CLI tools invoked by skills. **Tests in this plan are plain `python` assert scripts run with the venv interpreter** — matching repo style. Do NOT add pytest as a dependency.
- Venv python: `~/.claude/magang-tools/venv/bin/python` (has python-docx, pdfplumber).
- Source scripts live in `scripts/`; `install.sh` copies `scripts/*.py` → `~/.claude/magang-tools/scripts/`. During dev, **run scripts directly from the repo `scripts/` dir** with the venv python — no install needed to test.
- Config lives at `~/.claude/magang-tools/config.json` (already exists on this machine).
- Pedoman v6 PDF for extraction tests: `~/Documents/Berkas Magang Andika/Versi ke-6 Pedoman Laporan MBKM atau P3NK.pdf`.
- Shared DOCX helpers to copy/reuse from `scripts/generate_logbook.py`: `load_config`, `versioned_path`, `set_cell_border`, `set_fixed_layout`.

---

## File Structure

- **Create** `scripts/generate_penilaian.py` — DOCX generator for the penilaian penyelia form. Self-contained (own copies of the shared docx helpers, like the other generators).
- **Modify** `scripts/init_pedoman.py` — add `extract_penilaian_penyelia()` + wire into config dict.
- **Create** `skills/penilaian-penyelia/SKILL.md` — skill orchestration.
- **Modify** `README.md` — list the new command.
- **Modify** `CHANGELOG.md` — note the new skill + config key.
- **Create (temporary, dev only)** `/tmp/test_*.py` assert scripts — verification, not committed.

---

## Task 1: Pedoman extractor — `extract_penilaian_penyelia` in init_pedoman.py

**Files:**
- Modify: `scripts/init_pedoman.py` (add function after `extract_logbook_template`, ~line 181; wire into config dict in `main()` ~line 212)
- Test: `/tmp/test_extract_penilaian.py` (dev-only, not committed)

The 10 pedoman-v6 indicators (canonical, used as the fallback default):
```
Pemahaman terhadap tugas dan tanggung jawab
Penguasaan konsep dan teori yang relevan
Kemampuan dalam pemrograman / teknis
Penggunaan teknologi, tools, dan framework
Kualitas hasil kerja
Kemampuan analisis, pemecahan masalah & inisiatif
Komunikasi dan kolaborasi dalam tim
Manajemen waktu dan ketepatan penyelesaian tugas
Adaptasi terhadap lingkungan kerja dan perubahan
Etika, sikap profesional, dan tanggung jawab
```

- [ ] **Step 1: Write the failing test**

Create `/tmp/test_extract_penilaian.py`:
```python
import sys
sys.path.insert(0, "scripts")
from init_pedoman import extract_penilaian_penyelia, PENILAIAN_DEFAULT

# 1) Real pedoman text region → 10 indicators, none truncated mid-word.
sample = """Lampiran Form Lembar Penilaian Penyelia
----- KOP SURAT INSTITUSI MITRA ---------
No. Indikator Penilaian Nilai*)
1. Pemahaman terhadap tugas dan tanggung
jawab
2. Penguasaan konsep dan teori yang relevan
3. Kemampuan dalam pemrograman / teknis
4. Penggunaan teknologi, tools, dan framework
5. Kualitas hasil kerja
6. Kemampuan analisis, pemecahan masalah &
inisiatif
7. Komunikasi dan kolaborasi dalam tim
8. Manajemen waktu dan ketepatan
penyelesaian tugas
9. Adaptasi terhadap lingkungan kerja dan
perubahan
10. Etika, sikap profesional, dan tanggung jawab
Jumlah
Rata-rata
*) Skala/Rentang penilaian Penyelia 0 – 100.
"""
r = extract_penilaian_penyelia(sample)
inds = r["indicators"]
assert len(inds) == 10, f"expected 10, got {len(inds)}: {inds}"
assert inds[0] == "Pemahaman terhadap tugas dan tanggung jawab", inds[0]
assert inds[5] == "Kemampuan analisis, pemecahan masalah & inisiatif", inds[5]
assert inds[7] == "Manajemen waktu dan ketepatan penyelesaian tugas", inds[7]
assert all("\n" not in x for x in inds), "titles must be single-line"
assert r["scale"] == "0 – 100"
assert "title" in r and "note" in r

# 2) Garbage text → fallback default (10 canonical indicators).
r2 = extract_penilaian_penyelia("no relevant content here")
assert r2["indicators"] == PENILAIAN_DEFAULT["indicators"], "must fall back"
print("OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `~/.claude/magang-tools/venv/bin/python /tmp/test_extract_penilaian.py`
Expected: FAIL — `ImportError: cannot import name 'extract_penilaian_penyelia'`

- [ ] **Step 3: Write the implementation**

In `scripts/init_pedoman.py`, add module-level default constant (near the top, after the `ROMAN` dict ~line 43):
```python
PENILAIAN_DEFAULT = {
    "title": "PENILAIAN PELAKSANAAN KEGIATAN MBKM PROGRAM MSIB / P3NK (MAGANG MANDIRI)",
    "scale": "0 – 100",
    "note": "Jika sudah ada form dari instansi, form penilaian ini tidak berlaku.",
    "indicators": [
        "Pemahaman terhadap tugas dan tanggung jawab",
        "Penguasaan konsep dan teori yang relevan",
        "Kemampuan dalam pemrograman / teknis",
        "Penggunaan teknologi, tools, dan framework",
        "Kualitas hasil kerja",
        "Kemampuan analisis, pemecahan masalah & inisiatif",
        "Komunikasi dan kolaborasi dalam tim",
        "Manajemen waktu dan ketepatan penyelesaian tugas",
        "Adaptasi terhadap lingkungan kerja dan perubahan",
        "Etika, sikap profesional, dan tanggung jawab",
    ],
}
```

Add the extractor function (after `extract_logbook_template`, ~line 181):
```python
def extract_penilaian_penyelia(full_text: str) -> dict:
    """Extract the supervisor-assessment indicators from the 'Lembar Penilaian
    Penyelia' lampiran. Indicator titles wrap across lines in the PDF, so we
    join continuation lines until the next 'N.' marker. Falls back to the
    bundled pedoman-v6 default if parsing yields an unexpected count."""
    import copy
    result = copy.deepcopy(PENILAIAN_DEFAULT)

    # Locate the region: from the penilaian heading to the 'Jumlah' total row.
    start = re.search(r'Lembar\s+Penilaian\s+Penyelia', full_text, re.IGNORECASE)
    if not start:
        start = re.search(r'Indikator\s+Penilaian', full_text, re.IGNORECASE)
    if not start:
        return result
    region = full_text[start.end():]
    stop = re.search(r'\n\s*(Jumlah|Rata-?rata)\b', region)
    if stop:
        region = region[:stop.start()]

    # Parse numbered items, joining wrapped continuation lines.
    indicators = []
    current = None
    for raw in region.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r'^(\d{1,2})\.\s*(.*)$', line)
        if m:
            if current:
                indicators.append(current)
            current = m.group(2).strip()
        elif current is not None:
            # continuation line for the in-progress indicator
            current = (current + " " + line).strip()
    if current:
        indicators.append(current)

    # Clean whitespace; reject obviously-bad parses.
    indicators = [re.sub(r'\s+', ' ', x).strip() for x in indicators if x]
    if len(indicators) >= 5:
        result["indicators"] = indicators
    return result
```

Wire into the config dict in `main()` (after the `"logbook_template": ...` line, ~line 212):
```python
        "penilaian_penyelia": extract_penilaian_penyelia(full_text),
```

- [ ] **Step 4: Run test to verify it passes**

Run: `~/.claude/magang-tools/venv/bin/python /tmp/test_extract_penilaian.py`
Expected: `OK`

- [ ] **Step 5: Verify against the real pedoman PDF**

Run:
```bash
~/.claude/magang-tools/venv/bin/python scripts/init_pedoman.py \
  --pdf "$HOME/Documents/Berkas Magang Andika/Versi ke-6 Pedoman Laporan MBKM atau P3NK.pdf" \
  | ~/.claude/magang-tools/venv/bin/python -c "import json,sys; d=json.load(sys.stdin); pp=d['penilaian_penyelia']; print(len(pp['indicators']),'indicators'); [print(' ',i) for i in pp['indicators']]"
```
Expected: `10 indicators` printed, each a clean single-line title, no mid-word breaks (e.g. "...tanggung jawab" intact).

- [ ] **Step 6: Commit**

```bash
git add scripts/init_pedoman.py
git commit -m "feat(init): extract penilaian penyelia indicators from pedoman"
```

---

## Task 2: DOCX generator skeleton — config, args, blank form structure

**Files:**
- Create: `scripts/generate_penilaian.py`
- Test: `/tmp/test_gen_blank.py` (dev-only)

- [ ] **Step 1: Write the failing test**

Create `/tmp/test_gen_blank.py`:
```python
import json, subprocess, os, tempfile
from docx import Document

VENV = os.path.expanduser("~/.claude/magang-tools/venv/bin/python")
data = {
    "nama_penyelia": "Budi Santoso",
    "nama_institusi": "PT Contoh Teknologi",
    "nama_mahasiswa": "Andika Kurnia",
    "nim": "2001234",
    "waktu_pelaksanaan": "Feb 2026 - Jun 2026",
    "tempat_tanggal": "Bandung, 1 Juni 2026",
    "posisi_penyelia": "Lead Engineer",
}
dpath = tempfile.mktemp(suffix=".json")
opath = tempfile.mktemp(suffix=".docx")
open(dpath, "w").write(json.dumps(data))
out = subprocess.run([VENV, "scripts/generate_penilaian.py", "--data", dpath, "--output", opath],
                     capture_output=True, text=True)
assert out.returncode == 0, out.stderr
res = json.loads(out.stdout); assert res["success"]
doc = Document(res["output"])
alltext = "\n".join(p.text for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for c in row.cells:
            alltext += "\n" + c.text
assert "KOP SURAT INSTITUSI MITRA" in alltext
assert "PENILAIAN PELAKSANAAN KEGIATAN MBKM" in alltext
assert "Andika Kurnia" in alltext and "2001234" in alltext
assert "Budi Santoso" in alltext and "PT Contoh Teknologi" in alltext
assert "Indikator Penilaian" in alltext
assert "Pemahaman terhadap tugas dan tanggung jawab" in alltext
assert "Etika, sikap profesional, dan tanggung jawab" in alltext
assert "Jumlah" in alltext and "Rata-rata" in alltext
assert "0 – 100" in alltext
assert "tidak berlaku" in alltext
assert "Bandung, 1 Juni 2026" in alltext
# blank form: indicator table's Nilai cells empty
tbl = [t for t in doc.tables if any("Indikator" in c.text for c in t.rows[0].cells)][0]
nilai_col = [i for i,c in enumerate(tbl.rows[0].cells) if "Nilai" in c.text][0]
ind_rows = [r for r in tbl.rows[1:] if r.cells[1].text.strip() not in ("Jumlah","Rata-rata","")]
assert all(r.cells[nilai_col].text.strip() == "" for r in ind_rows), "blank form: nilai empty"
print("OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `~/.claude/magang-tools/venv/bin/python /tmp/test_gen_blank.py`
Expected: FAIL — `can't open file 'scripts/generate_penilaian.py'` / FileNotFound.

- [ ] **Step 3: Write the implementation**

Create `scripts/generate_penilaian.py`:
```python
#!/usr/bin/env python3
"""
Generate the official "Lembar Penilaian Penyelia" DOCX (pedoman v6) from JSON.
Blank form by default; fills scores + computes Jumlah/Rata-rata when `nilai`
is supplied. Mirrors generate_logbook.py conventions.

Usage: python generate_penilaian.py --data data.json --output out.docx
"""

import argparse
import json
import sys
from pathlib import Path


TOOLS_DIR = Path.home() / ".claude" / "magang-tools"
CONFIG_PATH = TOOLS_DIR / "config.json"

PENILAIAN_FALLBACK = {
    "title": "PENILAIAN PELAKSANAAN KEGIATAN MBKM PROGRAM MSIB / P3NK (MAGANG MANDIRI)",
    "scale": "0 – 100",
    "note": "Jika sudah ada form dari instansi, form penilaian ini tidak berlaku.",
    "indicators": [
        "Pemahaman terhadap tugas dan tanggung jawab",
        "Penguasaan konsep dan teori yang relevan",
        "Kemampuan dalam pemrograman / teknis",
        "Penggunaan teknologi, tools, dan framework",
        "Kualitas hasil kerja",
        "Kemampuan analisis, pemecahan masalah & inisiatif",
        "Komunikasi dan kolaborasi dalam tim",
        "Manajemen waktu dan ketepatan penyelesaian tugas",
        "Adaptasi terhadap lingkungan kerja dan perubahan",
        "Etika, sikap profesional, dan tanggung jawab",
    ],
}

INTRO = (
    "Dengan mempertimbangkan segala aspek, baik dari segi bobot pekerjaan maupun "
    "pelaksanaan kegiatan MBKM Program MSIB / P3NK (Magang Mandiri), maka kami "
    "memutuskan bahwa yang bersangkutan telah menyelesaikan kewajibannya, "
    "sebagaimana terinci dalam indikator penilaian sebagai berikut:"
)


def load_config() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def versioned_path(base: Path) -> Path:
    if not base.exists():
        return base
    v = 2
    while True:
        candidate = base.parent / f"{base.stem}_v{v}{base.suffix}"
        if not candidate.exists():
            return candidate
        v += 1


def set_cell_border(cell):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side in ("top", "left", "bottom", "right"):
        border = OxmlElement(f"w:{side}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "000000")
        tcBorders.append(border)
    tcPr.append(tcBorders)


def set_fixed_layout(table, widths):
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    tbl = table._tbl
    tblPr = tbl.tblPr
    for el in tblPr.findall(qn("w:tblLayout")):
        tblPr.remove(el)
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tblPr.append(layout)
    for el in tbl.findall(qn("w:tblGrid")):
        tbl.remove(el)
    grid = OxmlElement("w:tblGrid")
    for w in widths:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(w.twips)))
        grid.append(gc)
    tbl.insert(list(tbl).index(tblPr) + 1, grid)
    table.allow_autofit = False


def generate(data: dict, config: dict, output_path: Path) -> Path:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    pen = config.get("penilaian_penyelia") or PENILAIAN_FALLBACK
    indicators = pen.get("indicators") or PENILAIAN_FALLBACK["indicators"]
    title = pen.get("title", PENILAIAN_FALLBACK["title"])
    scale = pen.get("scale", "0 – 100")
    note = pen.get("note", PENILAIAN_FALLBACK["note"])

    fmt = config.get("formatting", {})
    margins = fmt.get("margins_cm", {"left": 4, "top": 3, "bottom": 3, "right": 3})
    font_name = fmt.get("font", "Arial")
    font_size = fmt.get("font_size_body", 11)

    doc = Document()
    sec = doc.sections[0]
    _pg = {"a4": (21.0, 29.7), "letter": (21.59, 27.94)}
    _pw, _ph = _pg.get(str(fmt.get("page_size", "A4")).lower(), (21.0, 29.7))
    sec.page_width = Cm(_pw); sec.page_height = Cm(_ph)
    sec.left_margin = Cm(margins["left"]); sec.right_margin = Cm(margins["right"])
    sec.top_margin = Cm(margins["top"]); sec.bottom_margin = Cm(margins["bottom"])

    printable = _pw - margins["left"] - margins["right"]  # cm

    def run_fmt(run, size=None, bold=False, italic=False, color=None):
        run.bold = bold; run.italic = italic
        run.font.name = font_name
        run.font.size = Pt(size or font_size)
        if color is not None:
            run.font.color.rgb = color

    def add_para(text, align=None, size=None, bold=False, italic=False,
                 color=None, space_after=2):
        p = doc.add_paragraph()
        if align is not None:
            p.alignment = align
        run_fmt(p.add_run(text), size, bold, italic, color)
        p.paragraph_format.space_after = Pt(space_after)
        return p

    # 1) KOP placeholder
    add_para("[ KOP SURAT INSTITUSI MITRA ]", align=WD_ALIGN_PARAGRAPH.CENTER,
             italic=True, color=RGBColor(0x80, 0x80, 0x80))
    doc.add_paragraph()

    # 2) Title
    add_para(title, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    doc.add_paragraph()

    # 3) Identity block (label | : | value), borderless
    fields = [
        ("Nama Penyelia", data.get("nama_penyelia", "")),
        ("Nama Institusi Mitra", data.get("nama_institusi", "")),
        ("Nama Mahasiswa", data.get("nama_mahasiswa", "")),
        ("Nomor Induk Mahasiswa", data.get("nim", "")),
        ("Waktu Pelaksanaan", data.get("waktu_pelaksanaan", "")),
    ]
    wlab, wcol = Cm(5.0), Cm(0.4)
    wval = Cm(max(printable - 5.0 - 0.4, 4.0))
    idt = doc.add_table(rows=len(fields), cols=3)
    set_fixed_layout(idt, [wlab, wcol, wval])
    for i, (label, value) in enumerate(fields):
        cells = idt.rows[i].cells
        for cell, w, txt in ((cells[0], wlab, label), (cells[1], wcol, ":"), (cells[2], wval, value)):
            cell.width = w
            p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            run_fmt(p.add_run(txt))
    doc.add_paragraph()

    # 4) Intro
    pi = add_para(INTRO, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6)
    doc.add_paragraph()

    # 5) Indicator table
    nilai = data.get("nilai") or {}
    # normalize keys to 1-based string indices
    nilai = {str(k): v for k, v in nilai.items()}
    w_no, w_nilai = 1.2, 2.2
    w_ind = max(printable - w_no - w_nilai, 5.0)
    widths = [Cm(w_no), Cm(w_ind), Cm(w_nilai)]
    n_rows = 1 + len(indicators) + 2  # header + indicators + Jumlah + Rata-rata
    tbl = doc.add_table(rows=n_rows, cols=3)
    tbl.style = "Table Grid"
    set_fixed_layout(tbl, widths)

    def cell_text(cell, text, w, align=None, bold=False):
        cell.width = w
        set_cell_border(cell)
        p = cell.paragraphs[0]
        if align is not None:
            p.alignment = align
        p.paragraph_format.space_after = Pt(0)
        run_fmt(p.add_run(text), bold=bold)

    # header
    hdr = tbl.rows[0].cells
    cell_text(hdr[0], "No.", widths[0], WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    cell_text(hdr[1], "Indikator Penilaian", widths[1], WD_ALIGN_PARAGRAPH.CENTER, bold=True)
    cell_text(hdr[2], "Nilai*)", widths[2], WD_ALIGN_PARAGRAPH.CENTER, bold=True)

    total = 0.0
    have_any = False
    for idx, ind in enumerate(indicators):
        row = tbl.rows[idx + 1].cells
        cell_text(row[0], str(idx + 1), widths[0], WD_ALIGN_PARAGRAPH.CENTER)
        cell_text(row[1], ind, widths[1])
        val = nilai.get(str(idx + 1), "")
        val_txt = ""
        if val != "" and val is not None:
            try:
                num = float(val)
                total += num; have_any = True
                val_txt = str(int(num)) if num == int(num) else str(num)
            except (TypeError, ValueError):
                val_txt = str(val)
        cell_text(row[2], val_txt, widths[2], WD_ALIGN_PARAGRAPH.CENTER)

    # Jumlah + Rata-rata (computed only when scores supplied; divisor fixed at 10-count)
    jumlah_txt = rata_txt = ""
    if have_any:
        avg = total / len(indicators)
        jumlah_txt = str(int(total)) if total == int(total) else str(round(total, 2))
        rata_txt = str(round(avg, 2))
    j = tbl.rows[1 + len(indicators)].cells
    cell_text(j[0], "", widths[0])
    cell_text(j[1], "Jumlah", widths[1], bold=True)
    cell_text(j[2], jumlah_txt, widths[2], WD_ALIGN_PARAGRAPH.CENTER)
    r = tbl.rows[2 + len(indicators)].cells
    cell_text(r[0], "", widths[0])
    cell_text(r[1], "Rata-rata", widths[1], bold=True)
    cell_text(r[2], rata_txt, widths[2], WD_ALIGN_PARAGRAPH.CENTER)

    # 6) Footnotes
    add_para(f"*) Skala/Rentang penilaian Penyelia {scale}.", size=font_size - 2, space_after=0)
    add_para(f"**) {note}", size=font_size - 2)

    # 7) Signature
    doc.add_paragraph()
    add_para(data.get("tempat_tanggal", ""), align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)
    add_para("Penyelia,", align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=0)
    sig = doc.add_table(rows=1, cols=1)
    tr = sig.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trH = OxmlElement("w:trHeight")
    trH.set(qn("w:val"), "1700"); trH.set(qn("w:hRule"), "atLeast")
    trPr.append(trH)
    name_line = data.get("nama_penyelia", "") or "______________________________________"
    add_para(name_line, align=WD_ALIGN_PARAGRAPH.RIGHT, bold=True, space_after=0)
    add_para("Tandatangan, Nama, Posisi, dan di Stempel",
             align=WD_ALIGN_PARAGRAPH.RIGHT, size=font_size - 2)

    output_path = versioned_path(output_path)
    doc.save(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    config = load_config()
    out = generate(data, config, Path(args.output).expanduser())
    print(json.dumps({"success": True, "output": str(out)}))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `~/.claude/magang-tools/venv/bin/python /tmp/test_gen_blank.py`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_penilaian.py
git commit -m "feat: add penilaian penyelia DOCX generator (blank form)"
```

---

## Task 3: Prefill scores + Jumlah/Rata-rata computation

**Files:**
- Modify: none (logic already in `generate_penilaian.py` from Task 2)
- Test: `/tmp/test_gen_prefill.py` (dev-only)

This task verifies the prefill branch written in Task 2. If the test fails, fix `generate_penilaian.py`.

- [ ] **Step 1: Write the failing test**

Create `/tmp/test_gen_prefill.py`:
```python
import json, subprocess, os, tempfile
from docx import Document

VENV = os.path.expanduser("~/.claude/magang-tools/venv/bin/python")
# all 10 = 80 each -> Jumlah 800, Rata-rata 80.0
data = {
    "nama_penyelia": "Budi", "nama_institusi": "PT X", "nama_mahasiswa": "Andika",
    "nim": "2001234", "waktu_pelaksanaan": "2026", "tempat_tanggal": "Bandung, 1 Juni 2026",
    "nilai": {str(i): 80 for i in range(1, 11)},
}
dpath = tempfile.mktemp(suffix=".json"); opath = tempfile.mktemp(suffix=".docx")
open(dpath, "w").write(json.dumps(data))
out = subprocess.run([VENV, "scripts/generate_penilaian.py", "--data", dpath, "--output", opath],
                     capture_output=True, text=True)
assert out.returncode == 0, out.stderr
doc = Document(json.loads(out.stdout)["output"])
tbl = [t for t in doc.tables if any("Indikator" in c.text for c in t.rows[0].cells)][0]
nilai_col = [i for i,c in enumerate(tbl.rows[0].cells) if "Nilai" in c.text][0]
rows = {r.cells[1].text.strip(): r for r in tbl.rows[1:]}
assert rows["Jumlah"].cells[nilai_col].text.strip() == "800", rows["Jumlah"].cells[nilai_col].text
assert rows["Rata-rata"].cells[nilai_col].text.strip() == "80.0", rows["Rata-rata"].cells[nilai_col].text
# a sample indicator row shows 80
ind_first = [r for r in tbl.rows[1:] if r.cells[0].text.strip() == "1"][0]
assert ind_first.cells[nilai_col].text.strip() == "80"

# partial prefill: only indicators 1 and 2 = 90, 70 -> Jumlah 160, Rata-rata 16.0 (divisor 10)
data2 = dict(data); data2["nilai"] = {"1": 90, "2": 70}
dpath2 = tempfile.mktemp(suffix=".json"); opath2 = tempfile.mktemp(suffix=".docx")
open(dpath2, "w").write(json.dumps(data2))
out2 = subprocess.run([VENV, "scripts/generate_penilaian.py", "--data", dpath2, "--output", opath2],
                      capture_output=True, text=True)
assert out2.returncode == 0, out2.stderr
doc2 = Document(json.loads(out2.stdout)["output"])
tbl2 = [t for t in doc2.tables if any("Indikator" in c.text for c in t.rows[0].cells)][0]
rows2 = {r.cells[1].text.strip(): r for r in tbl2.rows[1:]}
assert rows2["Jumlah"].cells[nilai_col].text.strip() == "160", rows2["Jumlah"].cells[nilai_col].text
assert rows2["Rata-rata"].cells[nilai_col].text.strip() == "16.0", rows2["Rata-rata"].cells[nilai_col].text
print("OK")
```

- [ ] **Step 2: Run test**

Run: `~/.claude/magang-tools/venv/bin/python /tmp/test_gen_prefill.py`
Expected: `OK` (logic from Task 2 already implements this). If FAIL, fix the Jumlah/Rata-rata branch in `generate_penilaian.py` until it passes.

- [ ] **Step 3: Commit (only if a fix was needed)**

```bash
git add scripts/generate_penilaian.py
git commit -m "fix: penilaian Jumlah/Rata-rata computation for prefill"
```
If no fix needed, skip — Task 2's commit already covers it.

---

## Task 4: SKILL.md orchestration

**Files:**
- Create: `skills/penilaian-penyelia/SKILL.md`

No automated test (Markdown orchestration). Verification is a structural read-through in Step 2.

- [ ] **Step 1: Write the skill file**

Create `skills/penilaian-penyelia/SKILL.md`:
````markdown
---
name: penilaian-penyelia
description: "Generate official Lembar Penilaian Penyelia (supervisor assessment form) DOCX per pedoman v6 — blank for hand-scoring or prefilled with scores"
argument-hint: "[--output-dir /path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Generate the official "Lembar Penilaian Penyelia" DOCX (pedoman v6 lampiran):
identity header, the pedoman's indicator table (Nilai 0–100), Jumlah & Rata-rata,
footnotes, and the supervisor signature block. Blank by default (printed on the
mitra's letterhead and scored by hand); optionally prefilled with scores the
student already holds. Output: Penilaian_Penyelia_[NamaMahasiswa].docx
</objective>

<constants>
CONFIG_PATH = ~/.claude/magang-tools/config.json
PYTHON      = ~/.claude/magang-tools/venv/bin/python
GEN_SCRIPT  = ~/.claude/magang-tools/scripts/generate_penilaian.py
</constants>

<steps>

## Step 1 — Check config

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
If missing → "Jalankan /rpl-magang:init dulu." Stop.

The generator reads `penilaian_penyelia` (indicators, scale, note) from config.
If an older config lacks that key, the generator uses the bundled pedoman-v6
default automatically — no re-init required (re-run /rpl-magang:init to refresh).

## Step 2 — Collect identity

If `config.json` has `student_identity`, use it as defaults (nama→nama_mahasiswa,
nim, mitra→nama_institusi, penyelia→nama_penyelia). Confirm, don't re-ask from zero.

Ask (batch with AskUserQuestion where sensible):
- Nama Penyelia (default from student_identity.penyelia)
- Nama Institusi Mitra (default from student_identity.mitra)
- Nama Mahasiswa (default from student_identity.nama)
- NIM (default from student_identity.nim)
- Waktu Pelaksanaan (contoh: "Februari 2026 – Juni 2026")
- Posisi Penyelia (contoh: "Lead Engineer")
- Tempat & tanggal tanda tangan (contoh: "Bandung, 1 Juni 2026")

## Step 3 — Blank or prefilled?

Ask: "Form mau dikosongin (penyelia isi nilai tangan) atau langsung diisi nilai?"
- Kosong → no `nilai` (default).
- Isi → ask the 10 indicator scores (0–100). Show the indicator list from
  config `penilaian_penyelia.indicators` so numbering matches. Build a
  `nilai` object keyed "1".."10".

## Step 4 — Generate DOCX

Write data JSON to `/tmp/penilaian_data_[timestamp].json`:
```json
{
  "nama_penyelia": "...",
  "nama_institusi": "...",
  "nama_mahasiswa": "...",
  "nim": "...",
  "waktu_pelaksanaan": "...",
  "posisi_penyelia": "...",
  "tempat_tanggal": "...",
  "nilai": {}
}
```
(`nilai` empty object = blank form; otherwise keys "1".."10".)

Output path: `--output-dir` if given, else current dir. Filename
`Penilaian_Penyelia_[NamaMahasiswa_tanpa_spasi].docx`.

Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_penilaian.py \
    --data /tmp/penilaian_data_[timestamp].json \
    --output "[output_path]"
```
Parse output JSON → final path (auto-versioned). Cleanup temp file.

## Step 5 — Summary

```
✅ Lembar Penilaian Penyelia berhasil dibuat!
  File : [output_path]
  Mode : [kosong / terisi]

Next steps:
  1. Cetak di atas KOP surat resmi institusi mitra (placeholder [ KOP ... ] dihapus/diganti)
  2. Kalau kosong: penyelia isi nilai tiap indikator (skala 0–100)
  3. Penyelia tanda tangan + tulis posisi + bubuhkan stempel
  Catatan: kalau institusi sudah punya form penilaian sendiri, form ini tidak berlaku.
```

</steps>
````

- [ ] **Step 2: Verify structure**

Run:
```bash
~/.claude/magang-tools/venv/bin/python -c "
import re, pathlib
t = pathlib.Path('skills/penilaian-penyelia/SKILL.md').read_text()
assert t.startswith('---'), 'missing frontmatter'
for k in ['name: penilaian-penyelia', 'allowed-tools', 'generate_penilaian.py', 'student_identity', 'Penilaian_Penyelia_']:
    assert k in t, f'missing: {k}'
print('OK')
"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add skills/penilaian-penyelia/SKILL.md
git commit -m "feat: add penilaian-penyelia skill"
```

---

## Task 5: End-to-end with installed layout + docs

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Deploy scripts to the tools dir and run E2E**

The skill calls `~/.claude/magang-tools/scripts/generate_penilaian.py`. Copy the
new/updated scripts there (simulating what install.sh does):
```bash
cp scripts/generate_penilaian.py scripts/init_pedoman.py ~/.claude/magang-tools/scripts/
```

Run a blank-form generation exactly as the skill would, into a temp dir:
```bash
printf '%s' '{"nama_penyelia":"Budi Santoso","nama_institusi":"PT Contoh","nama_mahasiswa":"Andika Kurnia","nim":"2001234","waktu_pelaksanaan":"Feb-Jun 2026","posisi_penyelia":"Lead Engineer","tempat_tanggal":"Bandung, 1 Juni 2026","nilai":{}}' > /tmp/pp_e2e.json
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_penilaian.py \
  --data /tmp/pp_e2e.json --output /tmp/Penilaian_Penyelia_AndikaKurnia.docx
```
Expected: `{"success": true, "output": "/tmp/Penilaian_Penyelia_AndikaKurnia.docx"}`

- [ ] **Step 2: Manually open & eyeball the DOCX**

Run: `open /tmp/Penilaian_Penyelia_AndikaKurnia.docx`
Confirm visually: KOP placeholder at top, centered bold title, aligned identity
colons, full-width bordered 10-row indicator table with empty Nilai column +
Jumlah/Rata-rata rows, footnotes, right-aligned signature block. Margins look
like 4cm left / 3cm others on A4.

- [ ] **Step 3: Update README**

In `README.md`, find the section listing the commands (logbook / laporan / pks).
Add a line for the new command in the same format/style as its siblings, e.g.:
```markdown
- `/rpl-magang:penilaian-penyelia` — generate Lembar Penilaian Penyelia (form penilaian dari pembimbing lapangan) sesuai pedoman, siap dicetak di KOP mitra
```
Read the surrounding lines first and match the exact existing bullet style
(emoji/wording) rather than pasting verbatim.

- [ ] **Step 4: Update CHANGELOG**

In `CHANGELOG.md`, add under the top/Unreleased (or next beta) section:
```markdown
### Added
- Skill `penilaian-penyelia`: generate the official Lembar Penilaian Penyelia DOCX
  (pedoman v6) — blank for hand-scoring or prefilled with auto-computed Jumlah & Rata-rata.
- `init` now extracts `penilaian_penyelia` indicators from the pedoman into config
  (with a pedoman-v6 default fallback for existing configs).
```
Match the existing CHANGELOG heading style (read the file first).

- [ ] **Step 5: Commit**

```bash
git add README.md CHANGELOG.md
git commit -m "docs: document penilaian-penyelia skill"
```

---

## Self-Review (completed during planning)

- **Spec coverage:** generator (Task 2/3), init extraction + fallback (Task 1),
  SKILL.md flow incl. student_identity reuse & blank/prefill (Task 4), README +
  CHANGELOG (Task 5), deployment via install.sh glob (Task 5 simulates the copy).
  All spec sections mapped.
- **Type/name consistency:** config key `penilaian_penyelia` and its fields
  (`title`, `scale`, `note`, `indicators`) identical across init_pedoman.py and
  generate_penilaian.py. Data keys (`nama_penyelia`, `nama_institusi`,
  `nama_mahasiswa`, `nim`, `waktu_pelaksanaan`, `posisi_penyelia`,
  `tempat_tanggal`, `nilai`) identical across generator, tests, and SKILL.md.
  Rata-rata divisor = `len(indicators)` (10) everywhere.
- **Placeholders:** none — all code and test bodies are complete.
- **Note:** `posisi_penyelia` is collected by the skill and stored in data but the
  pedoman prints position only via the static caption "Tandatangan, Nama, Posisi,
  dan di Stempel"; keeping the field captured is harmless and future-proof. Not a gap.
