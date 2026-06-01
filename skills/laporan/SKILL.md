---
name: laporan
description: "Write internship report (Laporan MBKM/P3NK) section by section with AI-assisted writing. Compiles all sections to single DOCX."
argument-hint: "[bab1|bab2|bab3|bab4|cover|lembar-pengesahan|kata-pengantar|compile] [--output-dir /path]"
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

<rpl-emphasis-rule>
Read `rpl_emphasis` from config. It applies to EVERY chapter (Bab I–IV), not just Bab III.

Before writing each bab, surface this as a REMINDER to the student (never a hard rule, never reject their input):

> 💡 Ingat: tonjolkan sisi Rekayasa Perangkat Lunak / software engineering di bab ini. Walau peran kamu non-coding (admin, desain, QA, ops), tarik benang ke aspek SE — analisis kebutuhan, desain, tooling/otomasi, pengujian, proses, atau kualitas software.

When the student's answers have a weak or missing RPL/SE angle, gently prompt with a concrete example for their role (e.g. admin → otomasi laporan & manajemen data sebagai artefak SE; desain grafis → design system, UI/UX, handoff ke developer). Then let them decide — proceed with whatever they choose.
</rpl-emphasis-rule>

<image-rule>
Laporan magang sebaiknya punya dokumentasi visual, bukan teks saja — foto aktivitas kerja, meeting tim, deliverable, screenshot fitur, dll. Gambar boleh di bab manapun + lampiran.

Sintaks di file .md (gambar HARUS berdiri sendiri di satu baris):
```markdown
![Deskripsi singkat gambar](path/ke/gambar.jpg)
```
- Path relatif → relatif ke output-dir (folder section). Absolut juga boleh.
- Engine `generate_laporan.py` otomatis: embed gambar lebar 14cm (fit halaman, proporsi terjaga), kasih caption ter-nomor "Gambar [bab].[urut]" (mis. Bab III → Gambar 3.1, 3.2; Lampiran → Gambar L.1), center.
- Kalau file gambar tidak ada → engine tulis placeholder "[Gambar tidak ditemukan: ...]" (tidak crash), nomor caption tetap jalan.

Saat menulis tiap bab (terutama Bab III), TANYA mahasiswa: "Punya foto dokumentasi buat bab ini? (aktivitas/meeting/deliverable/screenshot) — kasih path + deskripsi singkat." Lalu sisipkan `![deskripsi](path)` di posisi yang relevan dalam .md. Reminder, bukan wajib.
</image-rule>

<steps>

## Step 1 — Check config and determine mode

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
If missing → "Jalankan /rpl-magang:init dulu." Stop.

Read `config.document_structure.bagian_isi` to get the bab list (keys like `babI`, `babII`, ... → map to `bab1`, `bab2`, ...).

Check `$ARGUMENTS` for section name or `compile`:
- valid bab args: `bab1` through `bab[N]` based on config `bagian_isi` keys
- other valid args: `cover`, `lembar-pengesahan`, `kata-pengantar`, `compile`
- If none → ask: "Mau kerjain section apa?" and list available babs from config + cover/lembar-pengesahan/kata-pengantar/compile

When mode is `compile`, before running, check the required front-matter sections from config `document_structure.bagian_awal` (e.g. Halaman Judul → cover, Lembar Pengesahan → lembar-pengesahan). If a `.md` for a required section is missing in the output dir, warn: "⚠️ [Section] belum dibuat — sesuai pedoman ini wajib. Buat dulu? (mis. /rpl-magang:laporan lembar-pengesahan)". Let user proceed or stop.

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

Cover follows the pedoman exactly (Lampiran Contoh Cover) — a full one-page layout with fixed font sizes (12/10/12/14pt) and the UPI logo. The engine renders this from key:value data; do NOT write prose markdown here.

First read `student_identity` from `config.json`; if present, prefill Nama/NIM
(only confirm, don't re-ask). Then ask for what's missing:
- Nama Mahasiswa lengkap (kalau belum ada di config)
- NIM (kalau belum ada di config)
- Tahun

Generate `cover.md` as key:value data only:
```
nama: [Nama Mahasiswa]
nim: [NIM]
tahun: [Tahun]
```
The engine handles title, "Diajukan...", logo (from `~/.claude/magang-tools/assets/upi-logo.png` if present, else "LOGO UPI" placeholder), and the KAMPUS/PROGRAM/UNIVERSITAS/Tahun block — all sized per pedoman, full page.

## Step 3b — LEMBAR PENGESAHAN

Required front-matter per pedoman (config `bagian_awal` lists "Lembar Pengesahan"). Fixed template (Lampiran Contoh Lembar Pengesahan, hal. 14) — rendered by the DOCX engine from 4 key:value fields.

Ask:
- Nama Dosen Pembimbing (+ gelar)
- Nama Penyelia (dari mitra)
- Nama Ketua Program Studi RPL (kaprodi)
- NIP Ketua Program Studi

Write `lembar-pengesahan.md` with EXACTLY these 4 lines — nothing else.
No headings, no prose, no tables, no markdown formatting, no extra fields:
```
dosen_pembimbing: [Nama + gelar]
penyelia: [Nama penyelia]
kaprodi: [Nama kaprodi + gelar]
kaprodi_nip: [NIP]
```

The DOCX engine automatically renders the full page: title (14pt), "Lembar Pengesahan" (12pt),
"Diajukan sebagai salah satu syarat kegiatan MBKM..." (10pt), "Dosen Pembimbing :" and
"Penyelia :" lines with names, "Mengetahui, Ketua Program Studi ...", and signature block.
Do NOT reproduce any of that content in the .md file — the engine owns the layout.

## Step 4 — KATA PENGANTAR

Ask: names of dosen pembimbing, penyelia, and any others to thank.

Generate `kata-pengantar.md`. Start with the front-matter title as an H1
so the engine renders it centered + bold like the BAB titles:
```markdown
# KATA PENGANTAR
```
Then the formal opening-letter body:
- Puji syukur kepada Allah SWT
- Tujuan laporan
- Terima kasih kepada: Kaprodi, Dosen Pembimbing, Penyelia, orang tua, rekan
- Harapan penulis
- Tanda tangan block (kota, tanggal, penulis)

> Front-matter section titles (KATA PENGANTAR, DAFTAR ISI, DAFTAR PUSTAKA,
> LAMPIRAN) always use `# ` (H1 → centered, bold, chapter size), same as
> BAB titles. Never `##`.

## Step 5 — BAB content (config-driven)

For `bab1`, `bab2`, `bab3`, `bab4` (and any additional babs in config):

**Load bab structure from config:**
Read `config.document_structure.bagian_isi`. Map argument to key:
`bab1 → babI`, `bab2 → babII`, `bab3 → babIII`, `bab4 → babIV`

Get `title` (bab heading) and `sections[]` from that key.

**Write chapter heading in .md:**
```markdown
# [BAB TITLE from config, uppercase]
```

**For each section in `sections[]` (config order):**

Write sub-section heading then ask user for content:
```markdown
## [section.number] [section.title]
```

**Writing hints by section title keywords:**

| Keyword(s) in title | What to ask | Output format |
|---------------------|-------------|---------------|
| Latar Belakang | fenomena/masalah RPL yang memotivasi, relevansi perusahaan, tujuan belajar | 3–4 paragraphs; end: "...mendapat justifikasi untuk berkegiatan MBKM di [perusahaan]." |
| Manfaat, Tujuan | manfaat dan tujuan magang | numbered list: Manfaat 1.dst, Tujuan 1.dst |
| Waktu dan Tempat | tanggal mulai/akhir, alamat, divisi | paragraph + table: Waktu \| Tempat \| Divisi |
| Ruang Lingkup | cakupan dan batasan kegiatan | paragraph + bullet list |
| Gambaran Umum | sejarah, visi/misi, struktur org, skala | 2–3 paragraphs |
| Bidang Kerja, Usaha, Layanan | produk/layanan perusahaan | 1–2 paragraphs + list produk/layanan |
| Peran Mahasiswa | judul role, tim, tanggung jawab | paragraph + numbered list tanggung jawab |
| Jadwal | rencana aktivitas per bulan | table: No \| Kegiatan \| Bulan 1 \| Bulan 2 \| ... |
| Rencana, Jobdesk, Deskripsi Project | project/task yang ditugaskan, deliverable | paragraph + jobdesk list |
| Implementasi, Proses | metodologi, sprint/milestone, kolaborasi | narrative per project/sprint; sertakan metodologi (Agile/Scrum/dll) |
| Teknologi, Metode | bahasa, framework, tools | table: Kategori \| Teknologi/Tools \| Kegunaan |
| Hasil, Pencapaian | yang di-deliver/shipped, metrik | list deliverable + deskripsi |
| Judul Tugas Akhir | topik TA berdasarkan pengalaman | table: No \| Usulan Judul TA \| Deskripsi Singkat |
| Kesimpulan | capaian, skill berkembang, relevansi kurikulum RPL | 3–5 paragraphs |
| Saran | konteks dari mahasiswa | saran untuk: (1) mahasiswa magang selanjutnya, (2) Prodi RPL UPI Cibiru, (3) perusahaan mitra |

If section title matches no keyword → ask user what they want covered, write appropriate academic prose.

**Bab III special rule** (when `sections_flexible: true` in config):
- First ask: "Jenis magang / role kamu apa? (mis. software dev, QA, data, desain grafis, admin/ops, dll)"
- Coding-heavy role → use config sections as-is.
- Non-coding role → suggest adapted section titles that surface SE/RPL angle (process, tooling, requirements, quality, automation). Confirm with student before writing.
- Apply `<image-rule>` at end of Bab III: ask for documentation photos. Insert `![deskripsi](path)` on its own line near relevant sub-section.

Save as `bab[N].md` matching the argument.

## Step 9 — Confirm and suggest next step

After saving any section:
```
✅ [section] disimpan: [path].md

Progress:
  [list all bab files from config bagian_isi, cover.md, kata-pengantar.md — ✅ if .md exists in output_dir, ⬜ if not]

Jalankan /rpl-magang:laporan compile untuk export ke DOCX.
```

Check which `.md` files exist in the output dir to show accurate ✅/⬜ status:
```bash
ls [output_dir]/*.md 2>/dev/null
```

</steps>
