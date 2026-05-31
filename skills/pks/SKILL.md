---
name: pks
description: "Generate PKS (Cooperation Agreement / Perjanjian Kerja Sama) DOCX between UPI Cibiru RPL and a partner company"
argument-hint: "[--company CompanyName] [--output-dir /path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Generate a complete PKS (Perjanjian Kerja Sama / Cooperation Agreement) DOCX between Software Engineering Major UPI Cibiru and a partner company. Fills the standard 9-article structure. Output: PKS_[Company].docx
</objective>

<constants>
CONFIG_PATH = ~/.claude/magang-tools/config.json
PYTHON      = ~/.claude/magang-tools/venv/bin/python
PKS_SCRIPT  = ~/.claude/magang-tools/scripts/generate_pks.py
</constants>

<steps>

## Step 1 — Check config

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```
If missing → "Jalankan /rpl-magang:init dulu." Stop.

Load config to get `pks_template_path` (null = use built-in).

## Step 2 — Collect company information

Ask:
- Nama perusahaan lengkap (contoh: PT Fliptech Lentera Inspirasi Pertiwi)
- Alamat lengkap perusahaan
- Nama penandatangan dari perusahaan (Pihak Kedua)
- Jabatan penandatangan (contoh: Head of Engineering Consumer)
- Email perusahaan
- Nomor telepon perusahaan
- Fax perusahaan (ketik "-" kalau tidak ada)

## Step 3 — Collect UPI signatory information

Ask (or use defaults):
- Nama penandatangan UPI (default: KARIM SURYADI)
- Jabatan UPI (default: Director, Kampus UPI di Cibiru)
- Nomor dokumen UPI (format: ___ / ___ — bisa diisi setelah TTD)
- Nomor dokumen perusahaan (sama, bisa kosong dulu)

## Step 4 — Agreement date

Ask: "Tanggal PKS? (contoh: Senin, 1 Juni 2026 / Monday, the First of June, Two Thousand and Twenty-Six)"

## Step 5 — Correspondence details

Ask if different from company info already collected:
- UPI address (default: Jl. Pendidikan No. 15, Cibiru Wetan, Kec. Cileunyi, Kabupaten Bandung, West Java 40625)
- UPI phone (default: (022) 7801840)
- UPI fax (default: (022) 7830426)
- UPI email (default: rpl_cibiru@upi.edu)
- Confirm company correspondence (phone/email/fax from Step 2)

## Step 6 — Generate DOCX

Build data dict from collected inputs.
Write to temp file: `/tmp/pks_data_[timestamp].json`

Determine output path:
- If `--output-dir` in args → use that
- Default → current working directory
- Filename: `PKS_[CompanyName_no_spaces].docx`

Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_pks.py \
    --data /tmp/pks_data_[timestamp].json \
    --output "[output_path]" \
    [--template [pks_template_path] if not null]
```

Parse output JSON → get final path (auto-versioned if file existed).
Cleanup temp file.

## Step 7 — Summary

```
✅ PKS berhasil dibuat!
  File   : [output_path]
  Pihak 1: KARIM SURYADI (Director, UPI Cibiru)
  Pihak 2: [signatory] ([title], [company])
  Tanggal: [date]

Next steps:
  1. Buka DOCX, sisipkan logo UPI dan logo perusahaan secara manual
  2. Isi nomor dokumen kedua pihak (kalau belum)
  3. Print 2 rangkap, tempel materai, tanda tangan kedua pihak
  4. Scan → simpan sebagai PKS_[NamaPerusahaan].pdf
  5. Submit sesuai requirement: PKS_NamaPerusahaan.docx/pdf
```

</steps>
