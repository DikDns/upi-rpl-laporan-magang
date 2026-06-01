---
name: laporan-compile
description: "Compile semua section .md jadi satu DOCX laporan — DAFTAR ISI otomatis, page numbering Roman/Arabic"
argument-hint: "[--output-dir /path/to/laporan-draft]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Compile semua section .md di output dir menjadi satu DOCX laporan MBKM lengkap.
DAFTAR ISI dibuat otomatis (Word TOC field). Page numbering: i/ii/iii untuk front matter,
1/2/3 mulai dari BAB I. Cover tidak ada nomor halaman.
</objective>

<constants>
CONFIG_PATH    = ~/.claude/magang-tools/config.json
PYTHON         = ~/.claude/magang-tools/venv/bin/python
COMPILE_SCRIPT = ~/.claude/magang-tools/scripts/generate_laporan.py
</constants>

<steps>

## Step 1 — Cek config

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
Jika missing → "Jalankan /rpl-magang:init dulu." Stop.

## Step 2 — Tentukan output dir dan nama file

Cek `$ARGUMENTS` untuk `--output-dir`. Default: `./laporan-draft/`

Baca `config.file_naming.laporan` untuk nama file output default.
Jika `student_identity.nama` ada di config, ekspansi `{nama_mhs}` → nama mahasiswa.
Default: `Laporan_MBKM.docx`

## Step 3 — Cek section yang sudah ada

```bash
ls [output_dir]/*.md 2>/dev/null
```

Cek section wajib dari `config.document_structure.bagian_awal`:
- Halaman Judul → `cover.md`
- Lembar Pengesahan → `lembar-pengesahan.md`
- Kata Pengantar → `kata-pengantar.md`

Jika ada yang belum ada, tampilkan warning:
```
⚠️ [Section] belum dibuat — sesuai pedoman ini wajib ada.
   Buat dulu dengan /rpl-magang:laporan [section] atau lanjut tanpa itu?
```
Tunggu konfirmasi user sebelum compile.

## Step 4 — Compile

```bash
~/.claude/magang-tools/venv/bin/python \
  ~/.claude/magang-tools/scripts/generate_laporan.py \
  --sections-dir [output_dir] \
  --output [output_filename]
```

Parse JSON output. Jika error → tampilkan pesan error, stop.

## Step 5 — Konfirmasi

Tampilkan:
```
✅ Laporan berhasil di-compile!

Output : [output_path]
Ukuran : [file_size]

📋 Langkah selanjutnya:
  1. Buka file di Microsoft Word
  2. Klik kanan di bagian DAFTAR ISI → "Update Field" → "Update entire table"
     (ini mengisi nomor halaman dan hyperlink otomatis)
  3. Cek page numbering: cover (tidak ada nomor), front matter (i, ii, iii...),
     BAB I dst. (1, 2, 3...)
  4. Simpan dan kirim sesuai ketentuan P3NK
```

</steps>
