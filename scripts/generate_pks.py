#!/usr/bin/env python3
"""
Generate PKS (Cooperation Agreement) DOCX from JSON data.
Builds from scratch; optionally fills a user-provided template.
Usage: python generate_pks.py --data /path/to/data.json --output PKS_Company.docx [--template /path/to/template.docx]
"""

import argparse
import json
import sys
from pathlib import Path


TOOLS_DIR   = Path.home() / ".claude" / "magang-tools"
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


def build_pks(data: dict, output_path: Path) -> Path:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = Document()
    sec = doc.sections[0]
    sec.left_margin   = Cm(3)
    sec.right_margin  = Cm(3)
    sec.top_margin    = Cm(3)
    sec.bottom_margin = Cm(3)

    FONT  = "Times New Roman"
    FSIZE = 12

    def centered_bold(text, size=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.name = FONT
        run.font.size = Pt(size or FSIZE)
        p.paragraph_format.space_after = Pt(4)
        return p

    def centered(text, size=None):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(size or FSIZE)
        p.paragraph_format.space_after = Pt(4)
        return p

    def body(text, indent=False):
        p = doc.add_paragraph()
        if indent:
            p.paragraph_format.first_line_indent = Cm(1)
        run = p.add_run(text)
        run.font.name = FONT
        run.font.size = Pt(FSIZE)
        p.paragraph_format.space_after = Pt(6)
        return p

    def article_heading(num, title):
        doc.add_paragraph()
        centered_bold(num)
        centered_bold(title)

    def hr():
        doc.add_paragraph()

    # ── HEADER ───────────────────────────────────────────────
    centered_bold("COOPERATION AGREEMENT", 14)
    centered("BETWEEN", 12)
    doc.add_paragraph()
    centered_bold("SOFTWARE ENGINEERING MAJOR", 12)
    centered_bold("Kampus UPI di Cibiru", 12)
    centered_bold("UNIVERSITAS PENDIDIKAN INDONESIA", 12)
    centered("AND", 12)
    doc.add_paragraph()
    centered_bold(data.get("company_name", "").upper(), 12)
    doc.add_paragraph()

    # ── DOCUMENT NUMBERS ────────────────────────────────────
    body(f"NUMBER: {data.get('upi_number', '___ / ___')}")
    body(f"NUMBER: {data.get('company_number', '___ / ___')}")
    doc.add_paragraph()
    centered_bold("REGARDING")
    centered_bold("THE IMPLEMENTATION OF HIGHER EDUCATION TRIDHARMA")
    hr()

    # ── OPENING ─────────────────────────────────────────────
    body(
        f"On this day, {data.get('agreement_date', 'Monday, the First of June, Two Thousand and Twenty-Six (01-06-2026)')}, "
        f"the undersigned:"
    )
    doc.add_paragraph()

    body(
        f"1. {data.get('upi_signatory_name', 'KARIM SURYADI').upper()} : "
        f"Director of Universitas Pendidikan Indonesia Kampus UPI di Cibiru, acting in his official capacity "
        f"pursuant to Rector's Decree of Universitas Pendidikan Indonesia, thereby authorized to act for and "
        f"on behalf of Universitas Pendidikan Indonesia Kampus UPI di Cibiru, headquartered at "
        f"{data.get('upi_address', 'Jalan Pendidikan No. 13, Cibiru Wetan, Kec. Cileunyi, Kabupaten Bandung, West Java 40625')}, "
        f"hereinafter referred to as PARTY ONE; and"
    )
    doc.add_paragraph()
    body(
        f"2. {data.get('company_signatory_name', '').upper()} : "
        f"{data.get('company_signatory_title', '')} of {data.get('company_name', '')}, "
        f"acting in his/her official capacity, authorized to act for and on behalf of {data.get('company_name', '')}, "
        f"headquartered at {data.get('company_address', '')}, "
        f"hereinafter referred to as PARTY TWO."
    )
    doc.add_paragraph()
    body(
        "PARTY ONE and PARTY TWO, collectively referred to as THE PARTIES, and individually referred to as "
        "PARTY, hereby agree to enter into a Cooperation Agreement regarding the implementation of "
        "Higher Education Tridharma."
    )

    # ── ARTICLE 1 ────────────────────────────────────────────
    article_heading("Article 1", "PURPOSE AND OBJECTIVES")
    body(
        "The purpose of this Cooperation Agreement is to realize the role of Higher Education in the "
        "implementation of Tridharma.",
        indent=True
    )
    body(
        "The objective of this Cooperation Agreement is to implement the Internship Program or equivalent "
        "Professional Experience Enhancement Program for Non-Education Fields (P3NK).",
        indent=True
    )

    # ── ARTICLE 2 ────────────────────────────────────────────
    article_heading("Article 2", "SCOPE")
    body(
        "The scope of this Cooperation Agreement covers the implementation of an internship program or equivalent "
        "Professional Experience Enhancement Program for Non-Education Fields (P3NK) for a minimum of one (1) full semester.",
        indent=True
    )

    # ── ARTICLE 3 ────────────────────────────────────────────
    article_heading("Article 3", "TERM")
    body(
        "(1) This Cooperation Agreement shall be valid for a period of two (2) years from the date of signing, "
        "and may be extended or terminated by mutual agreement of THE PARTIES."
    )
    body(
        "(2) Should either party wish to extend or terminate, written notice must be given no later than "
        "one (1) month prior to the intended date."
    )
    body(
        "(3) If the receiving party does not respond within one (1) month of receipt, the party shall be deemed "
        "to have agreed to the extension or termination."
    )

    # ── ARTICLE 4 ────────────────────────────────────────────
    article_heading("Article 4", "RIGHTS AND OBLIGATIONS")
    body("(1) PARTY ONE shall have the following rights and obligations:")
    body("a. Rights: to receive and utilize results of cooperation carried out by PARTY TWO.")
    body("b. Obligations: to facilitate the cooperation and provide guidance within its authority.")
    doc.add_paragraph()
    body("(2) PARTY TWO shall have the following rights and obligations:")
    body("a. Rights: to receive support for Higher Education Tridharma activities from PARTY ONE.")
    body("b. Obligations: to contribute expertise and submit results with supporting documents.")

    # ── ARTICLE 5 ────────────────────────────────────────────
    article_heading("Article 5", "IMPLEMENTATION")
    body(
        "Detailed implementation shall be followed up with an Operational Agreement between the "
        "Software Engineering Major (representing PARTY ONE) and "
        f"{data.get('company_name', 'PARTY TWO')} (representing PARTY TWO).",
        indent=True
    )

    # ── ARTICLE 6 ────────────────────────────────────────────
    article_heading("Article 6", "RESPONSIBLE PARTIES AND IMPLEMENTORS")
    body(
        f"The technical implementor for PARTY ONE is the Software Engineering Major, "
        f"and for PARTY TWO is {data.get('company_name', '')}.",
        indent=True
    )

    # ── ARTICLE 7 ────────────────────────────────────────────
    article_heading("Article 7", "CORRESPONDENCE")
    body(
        "All notifications, requests, and/or proposals made in connection with this Cooperation Agreement "
        "shall be submitted in writing and delivered in person or via facsimile to each PARTY at the addresses below:"
    )

    corr_table = doc.add_table(rows=6, cols=3)
    corr_table.style = "Table Grid"
    rows_data = [
        ["", "PARTY ONE", "PARTY TWO"],
        ["Organization", "Software Engineering Major, Kampus UPI di Cibiru", data.get("company_name", "")],
        ["Address",      data.get("upi_address", "Jl. Pendidikan No. 15, Cibiru Wetan, Kec. Cileunyi, Kabupaten Bandung, West Java 40625"),
                         data.get("company_address", "")],
        ["Phone",  data.get("upi_phone",  "(022) 7801840"),  data.get("company_phone", "")],
        ["Fax",    data.get("upi_fax",    "(022) 7830426"),  data.get("company_fax",   "-")],
        ["Email",  data.get("upi_email",  "rpl_cibiru@upi.edu"), data.get("company_email", "")],
    ]
    for i, row in enumerate(rows_data):
        for j, text in enumerate(row):
            cell = corr_table.cell(i, j)
            p = cell.paragraphs[0]
            run = p.add_run(text)
            run.font.name = FONT
            run.font.size = Pt(11)
            if i == 0:
                run.bold = True

    # ── ARTICLE 8 ────────────────────────────────────────────
    article_heading("Article 8", "MISCELLANEOUS")
    body(
        "Any matters not yet governed by this Cooperation Agreement shall be regulated subsequently by "
        "THE PARTIES in a Supplementary Agreement, which shall form an integral and inseparable part of "
        "this Cooperation Agreement and shall carry equal legal force.",
        indent=True
    )

    # ── ARTICLE 9 ────────────────────────────────────────────
    article_heading("Article 9", "CLOSING")
    body(
        f"(1) This Cooperation Agreement is signed in Kabupaten Bandung on "
        f"{data.get('agreement_date', '___')}, made in two (2) original copies, "
        f"duly stamped and signed by THE PARTIES, both of which carry equal legal force."
    )
    body(
        "(2) All costs arising from the implementation of this Cooperation Agreement shall be borne "
        "by each PARTY in accordance with applicable laws and regulations."
    )

    # ── SIGNATURE BLOCK ──────────────────────────────────────
    doc.add_page_break()
    sig_table = doc.add_table(rows=7, cols=2)
    rows_sig = [
        ["PARTY ONE",                           "PARTY TWO"],
        ["Kampus UPI di Cibiru",                data.get("company_name", "")],
        ["Universitas Pendidikan Indonesia",    ""],
        ["", ""],
        ["", ""],
        ["", ""],
        [data.get("upi_signatory_name", ""),    data.get("company_signatory_name", "")],
    ]
    sub_labels = ["Director", data.get("company_signatory_title", "")]
    for i, row in enumerate(rows_sig):
        for j, text in enumerate(row):
            cell = sig_table.cell(i, j)
            p = cell.paragraphs[0]
            run = p.add_run(text)
            run.font.name = FONT
            run.font.size = Pt(FSIZE)
            if i in (0, 6):
                run.bold = True

    output_path = versioned_path(output_path)
    doc.save(str(output_path))
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data",     required=True)
    parser.add_argument("--output",   required=True)
    parser.add_argument("--template", default=None, help="Optional .docx template to use instead of built-in")
    args = parser.parse_args()

    data   = json.loads(Path(args.data).read_text(encoding="utf-8"))
    config = load_config()

    # Template override: if provided, warn that template-fill is not yet supported
    if args.template:
        print(json.dumps({"warning": "Custom template fill not yet implemented. Using built-in structure."}),
              file=sys.stderr)

    out = build_pks(data, Path(args.output).expanduser())
    print(json.dumps({"success": True, "output": str(out)}))


if __name__ == "__main__":
    main()
