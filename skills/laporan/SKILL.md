---
name: laporan
description: "Tulis section front matter laporan magang: cover, lembar-pengesahan, kata-pengantar"
argument-hint: "[cover|lembar-pengesahan|kata-pengantar] [--output-dir /path]"
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

Check `$ARGUMENTS` for section name:
- valid args: `cover`, `lembar-pengesahan`, `kata-pengantar`
- If none → ask: "Mau kerjain section apa? (cover/lembar-pengesahan/kata-pengantar)"
  Jika user minta bab → "Gunakan /rpl-magang:laporan-bab-1 (atau bab-2, bab-3, bab-4) yang sudah di-generate pas init."
  Jika user minta compile → "Gunakan /rpl-magang:laporan-compile"

Ask for output directory if not in args (default: `./laporan-draft/`):
```bash
mkdir -p [output_dir]
```

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
"Diajukan sebagai salah satu syarat kegiatan MBKM..." (10pt), the "Dosen Pembimbing" and
"Penyelia" rows as a BORDERLESS alignment table (label | ':' | value, colons aligned),
"Mengetahui, Ketua Program Studi ...", and signature block.
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
- Tanda tangan block — WRAP it in a `[SIGN] ... [/SIGN]` block so the engine
  renders it as a borderless, right-positioned 2-column table (left empty,
  right = the lines). Put blank lines where the wet signature goes:
  ```
  [SIGN]
  [Kota], [Bulan Tahun]
  Penulis,



  [Nama Mahasiswa]
  [/SIGN]
  ```

> Front-matter section titles (KATA PENGANTAR, DAFTAR ISI, DAFTAR PUSTAKA,
> LAMPIRAN) always use `# ` (H1 → centered, bold, chapter size), same as
> BAB titles. Never `##`.

## Step 5 — DAFTAR PUSTAKA & in-text citations (APA)

The pedoman uses APA (`config.formatting.citation_style`). Every external or
factual claim — company facts/statistics, theory, methodology — MUST carry an
in-text citation `(Penulis, Tahun)` in the relevant bab .md AND a matching
entry in the reference list.

Generate `daftar-pustaka.md`:
- Start with `# DAFTAR PUSTAKA` (H1 → centered, appears in DAFTAR ISI).
- One paragraph per source, sorted alphabetically by author, APA-7 format.
  Italicise titles with `_..._`. The engine auto-applies a hanging indent to
  this section (passes `hanging_para=True` for `daftar-pustaka`).
- Keep sources real and verifiable; confirm year/edition with the student.

When writing each bab, flag uncited factual claims and offer to add a
`(Penulis, Tahun)` citation + a Daftar Pustaka entry.

## Step 9 — Confirm and suggest next step

After saving any section:
```
✅ [section] disimpan: [path].md

Progress:
  [list all bab files from config bagian_isi, cover.md, kata-pengantar.md — ✅ if .md exists in output_dir, ⬜ if not]

Jalankan /rpl-magang:laporan-compile untuk export ke DOCX.
```

Check which `.md` files exist in the output dir to show accurate ✅/⬜ status:
```bash
ls [output_dir]/*.md 2>/dev/null
```

</steps>
