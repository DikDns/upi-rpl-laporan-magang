#!/usr/bin/env python3
"""
Generate per-bab SKILL.md files from rpl-magang config.
Usage: python generate_bab_skills.py --config ~/.claude/magang-tools/config.json
                                      --output-dir ~/.claude/magang-tools/generated-skills
"""

import argparse
import json
import sys
from pathlib import Path

TOOLS_DIR   = Path.home() / ".claude" / "magang-tools"
CONFIG_PATH = TOOLS_DIR / "config.json"

BAB_MAP = {
    "babI":    ("bab1", "BAB I"),
    "babII":   ("bab2", "BAB II"),
    "babIII":  ("bab3", "BAB III"),
    "babIV":   ("bab4", "BAB IV"),
    "babV":    ("bab5", "BAB V"),
    "babVI":   ("bab6", "BAB VI"),
}

WRITING_HINTS_TABLE = """\
**Panduan format per tipe sub-section (match judul):**

| Keyword dalam judul | Yang perlu ditanya | Format output |
|--------------------|--------------------|---------------|
| Latar Belakang | fenomena/masalah RPL yang memotivasi, relevansi perusahaan, tujuan belajar | 3–4 paragraf; akhiri: "...mendapat justifikasi untuk berkegiatan MBKM di [perusahaan]." |
| Manfaat, Tujuan | manfaat dan tujuan magang | numbered list: Manfaat 1.dst, Tujuan 1.dst |
| Waktu dan Tempat | tanggal mulai/akhir, alamat, divisi | paragraf + tabel: Waktu \\| Tempat \\| Divisi |
| Ruang Lingkup | cakupan dan batasan kegiatan | paragraf + bullet list |
| Gambaran Umum | sejarah, visi/misi, struktur org, skala | 2–3 paragraf |
| Bidang Kerja, Usaha, Layanan | produk/layanan perusahaan | 1–2 paragraf + list produk/layanan |
| Peran Mahasiswa | judul role, tim, tanggung jawab | paragraf + numbered list tanggung jawab |
| Jadwal | rencana aktivitas per bulan | tabel: No \\| Kegiatan \\| Bulan 1 \\| Bulan 2 \\| ... |
| Rencana, Jobdesk, Deskripsi Project | project/task yang ditugaskan, deliverable | paragraf + jobdesk list |
| Implementasi, Proses | metodologi, sprint/milestone, kolaborasi | narasi per project/sprint; sertakan metodologi |
| Teknologi, Metode | bahasa, framework, tools | tabel: Kategori \\| Teknologi/Tools \\| Kegunaan |
| Hasil, Pencapaian | yang di-deliver/shipped, metrik | list deliverable + deskripsi |
| Judul Tugas Akhir | topik TA berdasarkan pengalaman | tabel: No \\| Usulan Judul TA \\| Deskripsi Singkat |
| Kesimpulan | capaian, skill berkembang, relevansi kurikulum RPL | 3–5 paragraf |
| Saran | konteks dari mahasiswa | saran untuk: (1) mahasiswa magang selanjutnya, (2) Prodi RPL UPI Cibiru, (3) perusahaan mitra |

Jika judul sub-section tidak cocok keyword di atas → tanya user apa yang ingin dibahas, lalu tulis prosa akademis yang sesuai.
"""

BAB3_FLEXIBILITY_NOTE = """\

## Catatan Bab III — `sections_flexible: true`

Sub-section di atas adalah DEFAULT dari pedoman, bukan template kaku.

Pertama tanya: "Jenis magang / role kamu apa? (mis. software dev, QA, data, desain grafis, admin/ops, dll)"
- Role coding-heavy → gunakan sub-section dari pedoman langsung.
- Role non-coding → tawarkan adaptasi judul yang tetap menonjolkan aspek SE/RPL (proses, tooling, requirements, quality, otomasi). Konfirmasi dulu sebelum menulis.
"""

IMAGE_RULE = """\
<image-rule>
Bab III sebaiknya punya dokumentasi visual — foto aktivitas kerja, meeting tim, deliverable, screenshot fitur.

Sintaks di file .md (gambar HARUS berdiri sendiri di satu baris):
```markdown
![Deskripsi singkat gambar](path/ke/gambar.jpg)
```
- Path relatif → relatif ke output-dir. Absolut juga boleh.
- Engine generate_laporan.py otomatis embed gambar 14cm lebar, kasih caption "Gambar 3.N", center.
- File tidak ada → placeholder "[Gambar tidak ditemukan: ...]" (tidak crash).

Di akhir Bab III, tanya: "Punya foto dokumentasi kegiatan? (suasana kerja, meeting, deliverable, screenshot) — kasih path + deskripsi tiap foto." Sisipkan `![deskripsi](path)` di posisi yang relevan. Reminder, bukan wajib.
</image-rule>

"""

SKILL_TEMPLATE = """\
---
name: laporan-{skill_name_dashed}
description: "Tulis {bab_label} {bab_title} — {section_titles_desc}"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Tulis {bab_label} laporan magang berdasarkan pedoman yang sudah di-init.
Simpan sebagai {filename}.md di output dir.
</objective>

<constants>
CONFIG_PATH = ~/.claude/magang-tools/config.json
OUTPUT_DIR  = ./laporan-draft/ (or from --output-dir arg)
</constants>

<ai-writing-rule>
User may input notes in ANY language (Bahasa Indonesia, English, or mixed). Claude ALWAYS outputs formal Bahasa Indonesia prose. Expand bullet points into full academic paragraphs. Use passive voice where appropriate. Foreign/technical terms in *italic*.
</ai-writing-rule>

<rpl-emphasis-rule>
Read `rpl_emphasis` from config. Before writing each sub-section, surface this reminder:

> 💡 Ingat: tonjolkan sisi Rekayasa Perangkat Lunak / software engineering. Walau peran kamu non-coding (admin, desain, QA, ops), tarik benang ke aspek SE — analisis kebutuhan, desain, tooling/otomasi, pengujian, proses, atau kualitas software.

Then proceed with whatever the student chooses.
</rpl-emphasis-rule>

{image_rule}<steps>

## Step 1 — Cek config dan output dir

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
Jika missing → "Jalankan /rpl-magang:init dulu." Stop.

Cek `$ARGUMENTS` untuk `--output-dir`. Default: `./laporan-draft/`
```bash
mkdir -p [output_dir]
```

## Step 2 — Tulis {bab_label}: {bab_title}

Tulis heading bab di awal file:
```markdown
# {bab_title_upper}
```

Untuk setiap sub-section berikut (diambil dari pedoman kamu), tanya user dan tulis kontennya:

{sections_block}

{writing_hints}
{bab3_note}
## Step 3 — Simpan dan konfirmasi

Tulis ke `{filename}.md` di output dir.

Tampilkan progress:
```bash
ls [output_dir]/*.md 2>/dev/null
```

```
✅ {filename}.md disimpan di [output_dir]/

Progress:
  [cek tiap .md yang ada — ✅ ada, ⬜ belum]

Jalankan /rpl-magang:laporan-compile untuk export ke DOCX.
```

</steps>
"""


def _sections_block(sections: list) -> str:
    lines = []
    for s in sections:
        lines.append(f"**{s['number']} {s['title']}**")
        lines.append(f"→ Tanya user tentang topik ini, tulis dalam prosa akademis Bahasa Indonesia.")
        lines.append("")
    return "\n".join(lines)


def _section_titles_desc(sections: list, max_chars: int = 80) -> str:
    titles = ", ".join(s["title"] for s in sections)
    if len(titles) > max_chars:
        titles = titles[:max_chars].rsplit(",", 1)[0] + "..."
    return titles


def _skill_name_dashed(skill_name: str) -> str:
    """Convert 'bab1' -> 'bab-1' for directory and skill name usage."""
    return skill_name.replace("bab", "bab-")


def render_bab_skill(bab_key: str, bab_data: dict, sections_flexible: bool) -> str:
    skill_name, bab_label = BAB_MAP[bab_key]
    bab_title = bab_data.get("title", bab_label)
    sections = bab_data.get("sections", [])
    filename = skill_name  # bab1, bab2, etc.

    is_bab3 = bab_key == "babIII"
    image_rule_block = IMAGE_RULE if is_bab3 else ""
    bab3_note = BAB3_FLEXIBILITY_NOTE if (is_bab3 and sections_flexible) else ""

    return SKILL_TEMPLATE.format(
        skill_name_dashed=_skill_name_dashed(skill_name),
        bab_label=bab_label,
        bab_title=bab_title,
        bab_title_upper=bab_title.upper(),
        filename=filename,
        section_titles_desc=_section_titles_desc(sections),
        sections_block=_sections_block(sections),
        writing_hints=WRITING_HINTS_TABLE,
        image_rule=image_rule_block,
        bab3_note=bab3_note,
    )


def generate_all(config: dict, output_dir: Path) -> list:
    bagian_isi = config.get("document_structure", {}).get("bagian_isi", {})
    sections_flexible = config.get("document_structure", {}).get("sections_flexible", False)
    generated = []
    for bab_key in BAB_MAP:
        if bab_key not in bagian_isi:
            continue
        skill_name, _ = BAB_MAP[bab_key]
        dir_name = f"laporan-{_skill_name_dashed(skill_name)}"  # laporan-bab-1
        skill_dir = output_dir / dir_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        content = render_bab_skill(bab_key, bagian_isi[bab_key], sections_flexible)
        skill_path.write_text(content, encoding="utf-8")
        generated.append(skill_path)
    return generated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_PATH))
    parser.add_argument("--output-dir", default=str(TOOLS_DIR / "generated-skills"))
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()
    if not config_path.exists():
        print(json.dumps({"error": f"Config not found: {config_path}"}))
        sys.exit(1)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir).expanduser()
    paths = generate_all(config, output_dir)
    print(json.dumps({"success": True, "generated": [str(p) for p in paths]}))


if __name__ == "__main__":
    main()
