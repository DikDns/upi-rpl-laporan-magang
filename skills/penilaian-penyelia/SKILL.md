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
