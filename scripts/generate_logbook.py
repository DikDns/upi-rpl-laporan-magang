#!/usr/bin/env python3
"""
Generate logbook DOCX from JSON data.
Usage: python generate_logbook.py --data /path/to/data.json --output /path/to/output.docx
"""

import argparse
import json
import sys
from pathlib import Path


TOOLS_DIR = Path.home() / ".claude" / "magang-tools"
CONFIG_PATH = TOOLS_DIR / "config.json"


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


def generate(data: dict, config: dict, output_path: Path) -> Path:
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    fmt = config.get("formatting", {})
    margins = fmt.get("margins_cm", {"left": 4, "top": 3, "bottom": 3, "right": 3})
    font_name = fmt.get("font", "Arial")
    font_size = fmt.get("font_size_body", 11)

    sec = doc.sections[0]
    sec.left_margin   = Cm(margins["left"])
    sec.right_margin  = Cm(margins["right"])
    sec.top_margin    = Cm(margins["top"])
    sec.bottom_margin = Cm(margins["bottom"])

    def add_centered_bold(text, size=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.name = font_name
        run.font.size = Pt(size or font_size)
        p.paragraph_format.space_after = Pt(2)
        return p

    def add_field(label, value):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        r1 = p.add_run(f"{label:<20}: ")
        r1.font.name = font_name
        r1.font.size = Pt(font_size)
        r2 = p.add_run(value)
        r2.font.name = font_name
        r2.font.size = Pt(font_size)

    # ── header ──
    tmpl = config.get("logbook_template", {})
    add_centered_bold(tmpl.get("title", "CATATAN HARIAN & KEHADIRAN PESERTA"))
    add_centered_bold(tmpl.get("subtitle",
        "KEGIATAN MBKM KEGIATAN PROGRAM MSIB / P3NK (MAGANG MANDIRI) PADA MITRA"))
    doc.add_paragraph()

    add_field("Nama Mahasiswa", data.get("nama_mahasiswa", ""))
    add_field("NIM",            data.get("nim", ""))
    add_field("Nama Mitra",     data.get("nama_mitra", ""))
    add_field("Nama Penyelia",  data.get("nama_penyelia", ""))
    doc.add_paragraph()

    # ── table ──
    entries = data.get("entries", [])
    cols = tmpl.get("table_columns", ["No.", "Tanggal", "Uraian Aktivitas", "Paraf Penyelia"])
    widths = [Cm(1.2), Cm(3.5), Cm(9.5), Cm(2.8)]

    table = doc.add_table(rows=1 + len(entries), cols=len(cols))
    table.style = "Table Grid"

    # Header row
    for i, (col, w) in enumerate(zip(cols, widths)):
        cell = table.rows[0].cells[i]
        cell.width = w
        set_cell_border(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(col)
        run.bold = True
        run.font.name = font_name
        run.font.size = Pt(font_size)

    # Data rows
    for idx, entry in enumerate(entries):
        row = table.rows[idx + 1]
        values = [
            str(idx + 1),
            entry.get("tanggal", ""),
            entry.get("uraian_aktivitas", ""),
            ""
        ]
        for j, (val, w) in enumerate(zip(values, widths)):
            cell = row.cells[j]
            cell.width = w
            set_cell_border(cell)
            p = cell.paragraphs[0]
            if j == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(val)
            run.font.name = font_name
            run.font.size = Pt(font_size)

    doc.add_paragraph()
    doc.add_paragraph()

    # ── signature block ──
    sig_roles = tmpl.get("signature_roles", ["Peserta", "Penyelia"])
    sig_names = [data.get("nama_mahasiswa", ""), data.get("nama_penyelia", "")]
    sig_table = doc.add_table(rows=6, cols=2)
    sig_rows = [
        [f"{sig_roles[0]},", f"{sig_roles[1]},"],
        ["", ""],
        ["", ""],
        ["", ""],
        ["", ""],
        sig_names,
    ]
    for i, row_data in enumerate(sig_rows):
        for j, text in enumerate(row_data):
            cell = sig_table.cell(i, j)
            p = cell.paragraphs[0]
            run = p.add_run(text)
            run.font.name = font_name
            run.font.size = Pt(font_size)
            if i == 5:
                run.bold = True

    output_path = versioned_path(output_path)
    doc.save(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",   required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    data   = json.loads(Path(args.data).read_text(encoding="utf-8"))
    config = load_config()
    out    = generate(data, config, Path(args.output).expanduser())
    print(json.dumps({"success": True, "output": str(out)}))


if __name__ == "__main__":
    main()
