#!/usr/bin/env python3
"""
Compile laporan section .md files into a single DOCX.
Usage: python generate_laporan.py --sections-dir ./laporan-draft --output Laporan_MBKM_Name.docx
"""

import argparse
import json
import re
import sys
from pathlib import Path


TOOLS_DIR   = Path.home() / ".claude" / "magang-tools"
CONFIG_PATH = TOOLS_DIR / "config.json"

SECTIONS_ORDER = [
    "cover",
    "lembar-pengesahan",
    "kata-pengantar",
    "daftar-isi",
    "bab1",
    "bab2",
    "bab3",
    "bab4",
    "daftar-pustaka",
    "lampiran",
]


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


def apply_inline(paragraph, text: str, font_name: str, font_size_pt):
    from docx.shared import Pt

    # Split on **bold** and *italic*
    parts = re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", text)
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        else:
            run = paragraph.add_run(part)
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)


def md_to_doc(doc, md_text: str, font_name: str, font_size: int,
              base_dir: Path = None, chapter_label: str = None,
              fig_counter: dict = None):
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    if fig_counter is None:
        fig_counter = {}

    # Usable width on A4 with 4cm/3cm margins ≈ 14cm.
    IMG_WIDTH = Cm(14)

    def add_image(alt_text: str, img_ref: str):
        # Resolve path relative to the section's directory.
        p = Path(img_ref).expanduser()
        if not p.is_absolute() and base_dir is not None:
            p = (base_dir / img_ref).resolve()
        # Figure number scoped to chapter label (e.g. "3" -> Gambar 3.1).
        key = chapter_label or "_"
        fig_counter[key] = fig_counter.get(key, 0) + 1
        n = fig_counter[key]
        caption = (f"Gambar {chapter_label}.{n}" if chapter_label
                   else f"Gambar {n}")
        if alt_text.strip():
            caption += f" {alt_text.strip()}"

        if not p.exists():
            warn = doc.add_paragraph()
            warn.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = warn.add_run(f"[Gambar tidak ditemukan: {img_ref}]")
            r.italic = True
            r.font.name = font_name
            r.font.size = Pt(font_size)
        else:
            pic_p = doc.add_paragraph()
            pic_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = pic_p.add_run()
            run.add_picture(str(p), width=IMG_WIDTH)

        cap_p = doc.add_paragraph()
        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cap_p.add_run(caption)
        cr.font.name = font_name
        cr.font.size = Pt(font_size - 1)
        cap_p.paragraph_format.space_after = Pt(6)

    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            i += 1
            continue

        # ── Image: ![caption](path) on its own line ──
        img_m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if img_m:
            add_image(img_m.group(1), img_m.group(2).strip())
            i += 1
            continue

        # ── Headings ──
        if line.startswith("# "):
            p = doc.add_heading(line[2:].strip(), level=1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = font_name
            i += 1
            continue

        if line.startswith("## "):
            p = doc.add_heading(line[3:].strip(), level=2)
            for run in p.runs:
                run.font.name = font_name
            i += 1
            continue

        if line.startswith("### "):
            p = doc.add_heading(line[4:].strip(), level=3)
            for run in p.runs:
                run.font.name = font_name
            i += 1
            continue

        # ── Bullet list ──
        if line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(style="List Bullet")
            apply_inline(p, line[2:].strip(), font_name, font_size)
            i += 1
            continue

        # ── Numbered list ──
        num_m = re.match(r"^(\d+)\.\s+(.+)", line)
        if num_m:
            p = doc.add_paragraph(style="List Number")
            apply_inline(p, num_m.group(2).strip(), font_name, font_size)
            i += 1
            continue

        # ── Table (markdown pipe table) ──
        if "|" in line:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            # Filter out separator rows (---|---)
            data_rows = [r for r in table_lines
                         if not re.match(r"^\s*[\|:\-\s]+$", r)]
            if data_rows:
                parsed = []
                for row in data_rows:
                    cells = [c.strip() for c in row.strip().strip("|").split("|")]
                    parsed.append(cells)
                if parsed:
                    max_cols = max(len(r) for r in parsed)
                    tbl = doc.add_table(rows=len(parsed), cols=max_cols)
                    tbl.style = "Table Grid"
                    for ri, row in enumerate(parsed):
                        for ci, cell_text in enumerate(row):
                            if ci < max_cols:
                                p = tbl.cell(ri, ci).paragraphs[0]
                                run = p.add_run(cell_text)
                                run.font.name = font_name
                                run.font.size = Pt(font_size)
                                if ri == 0:
                                    run.bold = True
            continue

        # ── Horizontal rule ──
        if re.match(r"^[-*_]{3,}$", line.strip()):
            doc.add_paragraph()
            i += 1
            continue

        # ── Regular paragraph ──
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.space_after = Pt(0)
        apply_inline(p, line.strip(), font_name, font_size)
        i += 1


def compile_sections(sections_dir: Path, output_path: Path, config: dict) -> Path:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.oxml.ns import qn

    fmt       = config.get("formatting", {})
    margins   = fmt.get("margins_cm", {"left": 4, "top": 3, "bottom": 3, "right": 3})
    font_name = fmt.get("font", "Arial")
    font_size = fmt.get("font_size_body", 11)
    spacing   = fmt.get("line_spacing", 1.5)

    doc = Document()

    sec = doc.sections[0]
    sec.left_margin   = Cm(margins["left"])
    sec.right_margin  = Cm(margins["right"])
    sec.top_margin    = Cm(margins["top"])
    sec.bottom_margin = Cm(margins["bottom"])

    # Default paragraph style
    style = doc.styles["Normal"]
    style.font.name = font_name
    style.font.size = Pt(font_size)
    # line_spacing as a float → WD_LINE_SPACING.MULTIPLE (e.g. 1.5x).
    # Passing a Length here would switch to EXACTLY mode and overflow.
    style.paragraph_format.line_spacing = spacing

    # Collect sections in order
    all_md = {f.stem: f for f in sections_dir.glob("*.md")}
    ordered = []
    for name in SECTIONS_ORDER:
        if name in all_md:
            ordered.append((name, all_md.pop(name)))
    for name, path in sorted(all_md.items()):
        ordered.append((name, path))

    # Figure numbering is shared across the whole document, scoped per
    # chapter label (bab3 -> "Gambar 3.x", lampiran -> "Gambar L.x").
    fig_counter = {}

    def chapter_label_for(name: str):
        m = re.search(r"bab(\d+)", name)
        if m:
            return m.group(1)
        if "lampiran" in name:
            return "L"
        return None

    for idx, (name, md_file) in enumerate(ordered):
        if idx > 0:
            doc.add_page_break()
        md_content = md_file.read_text(encoding="utf-8")
        md_to_doc(doc, md_content, font_name, font_size,
                  base_dir=sections_dir,
                  chapter_label=chapter_label_for(name),
                  fig_counter=fig_counter)

    output_path = versioned_path(output_path)
    doc.save(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sections-dir", required=True)
    parser.add_argument("--output",       required=True)
    args = parser.parse_args()

    sections_dir = Path(args.sections_dir).expanduser().resolve()
    if not sections_dir.exists():
        print(json.dumps({"error": f"Not found: {sections_dir}"}))
        sys.exit(1)

    config     = load_config()
    out        = compile_sections(sections_dir, Path(args.output).expanduser(), config)
    print(json.dumps({"success": True, "output": str(out)}))


if __name__ == "__main__":
    main()
