#!/usr/bin/env python3
"""
Parse pedoman PDF and extract configuration for rpl-magang skills.
Usage: python init_pedoman.py --pdf /path/to/pedoman.pdf [--output /path/to/config.json]
Exit codes: 0=success, 1=file not found, 2=parse failed (use fallback)
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


# ── PDF extraction ───────────────────────────────────────────

def extract_pdf_text(pdf_path: str) -> list[dict] | None:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pages.append({"page": i + 1, "text": text})
        return pages if pages else None
    except Exception:
        return None


def file_hash(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ── extractors ───────────────────────────────────────────────

def extract_structure(full_text: str) -> dict:
    structure = {"bagian_awal": [], "bagian_isi": {}, "bagian_akhir": []}

    # Bagian awal items
    awal_keywords = ["HALAMAN JUDUL", "LEMBAR PENGESAHAN", "KATA PENGANTAR",
                     "DAFTAR ISI", "DAFTAR TABEL", "DAFTAR GAMBAR"]
    for kw in awal_keywords:
        if kw in full_text.upper():
            structure["bagian_awal"].append(kw.title())

    # Chapters: "Bab I", "Bab II", etc.
    bab_re = re.compile(
        r'Bab\s+(I{1,4}|IV|VI{0,3}|V)[ \t]+([A-Z][A-Z /&]+)',
        re.MULTILINE
    )
    for m in bab_re.finditer(full_text):
        bab_key = f"bab{m.group(1).strip()}"
        structure["bagian_isi"][bab_key] = {
            "title": m.group(2).strip().title(),
            "sections": []
        }

    # Sub-sections: "1.1 Title"
    sec_re = re.compile(r'(\d+\.\d+)\s{1,4}([A-Za-z][^\n]{3,100})', re.MULTILINE)
    for m in sec_re.finditer(full_text):
        num = m.group(1).strip()
        title = m.group(2).strip()
        bab_num = num.split(".")[0]
        # Map to roman numeral key as found
        for key in structure["bagian_isi"]:
            # Simple heuristic: bab I -> 1, II -> 2, etc.
            roman_map = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}
            for roman, arabic in roman_map.items():
                if key == f"bab{roman}" and str(arabic) == bab_num:
                    structure["bagian_isi"][key]["sections"].append(
                        {"number": num, "title": title}
                    )

    # Bagian akhir
    for kw in ["Daftar Pustaka", "Lampiran"]:
        if kw.lower() in full_text.lower():
            structure["bagian_akhir"].append(kw)

    return structure


def extract_formatting(full_text: str) -> dict:
    fmt = {
        "font": "Arial",
        "font_size_body": 11,
        "font_size_chapter_title": 14,
        "font_size_section_title": 12,
        "line_spacing": 1.5,
        "margins_cm": {"left": 4, "top": 3, "bottom": 3, "right": 3},
        "citation_style": "APA",
        "paragraph_indent": "1 tab (5 ketukan dari tepi kiri)"
    }

    # Font name
    font_m = re.search(r'\b(Arial|Times New Roman|Calibri)\b', full_text)
    if font_m:
        fmt["font"] = font_m.group(1)

    # Font size
    size_m = re.search(r'(?:Arial|huruf)\s+(\d+)\s*(?:pt|point|poin)', full_text, re.IGNORECASE)
    if size_m:
        fmt["font_size_body"] = int(size_m.group(1))

    # Margins
    left_m = re.search(r'(\d+)\s*cm\s+dari\s+tepi\s+kiri', full_text)
    top_m  = re.search(r'(\d+)\s*cm\s+dari\s+tepi\s+atas', full_text)
    bot_m  = re.search(r'(\d+)\s*cm\s+dari\s+tepi\s+bawah', full_text)
    right_m = re.search(r'(\d+)\s*cm\s+dari\s+tepi\s+kanan', full_text)
    if left_m:  fmt["margins_cm"]["left"]   = int(left_m.group(1))
    if top_m:   fmt["margins_cm"]["top"]    = int(top_m.group(1))
    if bot_m:   fmt["margins_cm"]["bottom"] = int(bot_m.group(1))
    if right_m: fmt["margins_cm"]["right"]  = int(right_m.group(1))

    # Citation style
    if "APA" in full_text or "American Psychological" in full_text:
        fmt["citation_style"] = "APA"

    return fmt


def extract_assessment(full_text: str) -> list[str]:
    # Find the assessment section, then bound it at the next heading so we
    # don't bleed into the "Tata Tertib" rules that follow (also numbered).
    section_m = re.search(r'[Kk]omponen\s+[Pp]enilaian', full_text)
    if section_m:
        rest = full_text[section_m.end():]
        stop = re.search(
            r'\n\s*(Tata\s+Tertib|TATA\s+TERTIB|Bab\s+[IVX]|BAB\s+[IVX]|'
            r'LAMPIRAN|DAFTAR\s+PUSTAKA)',
            rest
        )
        if stop:
            rest = rest[:stop.start()]
        items = [i.strip() for i in re.findall(r'\d+\.\s+([^\n]+)', rest)]
        if items:
            return items

    # Default from known pedoman v6
    return [
        "Aspek kemampuan kompetensi dan ketrampilan",
        "Aspek personal dan sosial",
        "Aspek profesionalisme kerja",
        "Aspek portofolio",
        "Ujian Akhir (Ujian kinerja)"
    ]


def extract_logbook_template(full_text: str) -> dict:
    return {
        "title": "CATATAN HARIAN & KEHADIRAN PESERTA",
        "subtitle": "KEGIATAN MBKM KEGIATAN PROGRAM MSIB / P3NK (MAGANG MANDIRI) PADA MITRA",
        "header_fields": ["Nama Mahasiswa", "NIM", "Nama Mitra", "Nama Penyelia"],
        "table_columns": ["No.", "Tanggal", "Uraian Aktivitas", "Paraf Penyelia"],
        "signature_roles": ["Peserta", "Penyelia"]
    }


# ── main ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Parse pedoman PDF → rpl-magang config")
    parser.add_argument("--pdf", required=True, help="Path to pedoman PDF")
    parser.add_argument("--output", default=None, help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)

    pages = extract_pdf_text(str(pdf_path))
    if not pages:
        print(json.dumps({"error": "pdf_parse_failed"}))
        sys.exit(2)

    full_text = "\n".join(p["text"] for p in pages)

    config = {
        "pedoman_path": str(pdf_path),
        "pedoman_hash": file_hash(str(pdf_path)),
        "program": "Rekayasa Perangkat Lunak",
        "campus": "Kampus UPI di Cibiru",
        "document_structure": extract_structure(full_text),
        "formatting": extract_formatting(full_text),
        "assessment_criteria": extract_assessment(full_text),
        "logbook_template": extract_logbook_template(full_text),
        "pks_template_path": None,
        "rpl_emphasis": {
            "mode": "prompt",
            "scope": "all_chapters",
            "guidance": (
                "Tiap bab harus menonjolkan sisi Rekayasa Perangkat Lunak / "
                "software engineering dari kegiatan magang — walau peran "
                "non-coding (admin, desain grafis, QA, ops). Tarik benang ke: "
                "analisis kebutuhan, desain, implementasi/tooling, pengujian, "
                "proses, dan kualitas perangkat lunak. Ini reminder untuk "
                "mahasiswa, bukan aturan kaku — struktur boleh disesuaikan "
                "asalkan poin ke-RPL-an tetap menonjol."
            )
        }
    }
    # Default sections from pedoman are suggestions; students may adapt
    # ordering/titles to their internship type (esp. Bab III).
    config["document_structure"]["sections_flexible"] = True

    if args.output:
        out = Path(args.output).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"success": True, "output": str(out)}))
    else:
        print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
