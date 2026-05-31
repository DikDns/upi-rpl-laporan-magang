---
name: laporan
description: "Write internship report (Laporan MBKM/P3NK) section by section with AI-assisted writing. Compiles all sections to single DOCX."
argument-hint: "[bab1|bab2|bab3|bab4|cover|kata-pengantar|compile] [--output-dir /path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Guide user through writing their laporan magang section by section. Each section saved as .md draft. When all sections ready, compile to single DOCX with correct formatting from config.
</objective>

<constants>
CONFIG_PATH     = ~/.claude/magang-tools/config.json
PYTHON          = ~/.claude/magang-tools/venv/bin/python
LAPORAN_SCRIPT  = ~/.claude/magang-tools/scripts/generate_laporan.py
</constants>

<ai-writing-rule>
User may input notes in ANY language (Bahasa Indonesia, English, or mixed). Claude ALWAYS outputs formal Bahasa Indonesia prose. Expand bullet points into full academic paragraphs. Use passive voice where appropriate. Foreign/technical terms in *italic*.
</ai-writing-rule>

<steps>

## Step 1 — Check config and determine mode

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
If missing → "Jalankan /rpl-magang:init dulu." Stop.

Check `$ARGUMENTS` for section name or `compile`:
- `bab1`, `bab2`, `bab3`, `bab4`, `cover`, `kata-pengantar`, `compile`
- If none → ask: "Mau kerjain section apa? (bab1/bab2/bab3/bab4/cover/kata-pengantar/compile)"

Ask for output directory if not in args (default: `./laporan-draft/`):
```bash
mkdir -p [output_dir]
```

## Step 2 — COMPILE mode

If mode == `compile`:
1. List all .md files in the sections dir
2. Show: "Section yang akan di-compile: [list]"
3. Ask: "Nama file output? (default: Laporan_MBKM_[NamaMhs].docx)"
4. Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_laporan.py \
    --sections-dir "[sections_dir]" \
    --output "[output_path]"
```
5. Report final output path (auto-versioned).
6. Stop.

## Step 3 — COVER

Ask:
- Nama Mahasiswa lengkap
- NIM
- Tahun

Generate `cover.md`:
```markdown
# Laporan Pelaksanaan Kegiatan MBKM
## MBKM Program MSIB / P3NK (Magang Mandiri)

Diajukan sebagai salah satu syarat Kegiatan MBKM
pada Program Studi Rekayasa Perangkat Lunak

---
*[LOGO UPI — sisipkan gambar secara manual di Word]*
---

Oleh:
**[Nama Mahasiswa]**
[NIM]

KAMPUS UPI DI CIBIRU
REKAYASA PERANGKAT LUNAK
UNIVERSITAS PENDIDIKAN INDONESIA
[Tahun]
```

## Step 4 — KATA PENGANTAR

Ask: names of dosen pembimbing, penyelia, and any others to thank.

Generate `kata-pengantar.md` — formal opening letter style. Include:
- Puji syukur kepada Allah SWT
- Tujuan laporan
- Terima kasih kepada: Kaprodi, Dosen Pembimbing, Penyelia, orang tua, rekan
- Harapan penulis
- Tanda tangan block (kota, tanggal, penulis)

## Step 5 — BAB I (Pendahuluan)

Ask for each sub-section. User may answer in any language — Claude expands to full paragraphs.

**1.1 Latar Belakang** — ask:
- Fenomena/masalah di dunia RPL yang memotivasi magang ini?
- Mengapa perusahaan ini relevan?
- Apa yang ingin dipelajari?
→ Write 3–4 paragraphs. End with: "...sehingga mendapatkan justifikasi alasan untuk berkegiatan MBKM Program MSIB / P3NK di [perusahaan]."

**1.2 Manfaat & Tujuan** — ask what benefits and goals:
→ Write as numbered list (Manfaat, then Tujuan).

**1.3 Waktu dan Tempat Pelaksanaan** — ask start/end dates, company address, division:
→ Write as paragraph + table with: Waktu, Tempat, Divisi.

**1.4 Ruang Lingkup** — ask what was in scope / out of scope:
→ Write as paragraph + bullet list.

Save as `bab1.md`.

## Step 6 — BAB II (Profil Institusi Mitra)

**2.1 Gambaran Umum** — ask: history, vision/mission, org structure, company scale:
→ 2–3 paragraphs.

**2.2 Bidang Kerja / Usaha dan Layanan** — ask: what products/services does the company offer?
→ 1–2 paragraphs + list of main products/services.

**2.3 Peran Mahasiswa dalam Mitra** — ask: role title, team, responsibilities:
→ Paragraph + numbered list of tanggung jawab.

**2.4 Jadwal Kegiatan** — ask: monthly activity plan:
→ Generate markdown table:
| No | Kegiatan | Bulan 1 | Bulan 2 | Bulan 3 | Bulan 4 |

Save as `bab2.md`.

## Step 7 — BAB III (Pelaksanaan Kegiatan)

**3.1 Rencana Kegiatan / Jobdesk / Deskripsi Project** — ask: assigned projects/tasks, deliverables:
→ Overview paragraph + jobdesk list.

**3.2 Implementasi Kegiatan / Proses Project** — ask: methodology, sprint/milestone breakdown, collaboration:
→ Narrative with sub-sections per project/sprint. Include metodologi (Agile/Scrum/etc).

**3.3 Teknologi dan Metode** — ask: languages, frameworks, tools, methodologies:
→ Table: Kategori | Teknologi/Tools | Kegunaan

**3.4 Hasil Karya / Pencapaian Akhir** — ask: what was shipped/delivered, any metrics:
→ List of deliverables + description.

**3.5 List Judul Tugas Akhir** — ask: based on experience, suggest 3–5 potential TA topics:
→ Table: No | Usulan Judul TA | Deskripsi Singkat

Save as `bab3.md`.

## Step 8 — BAB IV (Kesimpulan dan Saran)

**4.1 Kesimpulan** — ask: what was achieved, skills developed, alignment with RPL curriculum:
→ 3–5 paragraphs.

**4.2 Saran** — ask for context, then generate saran for:
- Mahasiswa yang akan magang selanjutnya
- Program Studi RPL UPI Cibiru
- Perusahaan mitra

Save as `bab4.md`.

## Step 9 — Confirm and suggest next step

After saving any section:
```
✅ [section] disimpan: [path].md

Progress:
  ✅ bab1.md    ✅ bab2.md
  ⬜ bab3.md    ⬜ bab4.md
  ⬜ cover.md   ⬜ kata-pengantar.md

Jalankan /rpl-magang:laporan compile untuk export ke DOCX.
```

</steps>
