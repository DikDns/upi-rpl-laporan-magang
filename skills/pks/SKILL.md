---
name: pks
description: "Generate PKS (Cooperation Agreement / Perjanjian Kerja Sama) DOCX by filling the official UPI template's partner placeholders"
argument-hint: "[--company CompanyName] [--output-dir /path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Generate a PKS (Perjanjian Kerja Sama) DOCX by filling ONLY the partner-specific placeholders in the official UPI template — mirroring the manual workflow of replacing the yellow-highlighted fields in the reference PKS. The legal text (all pasal) and the PIHAK KESATU / UPI side stay verbatim. Output: PKS_[Company].docx
</objective>

<workflow-note>
This skill does NOT regenerate the agreement text. It fills a tokenized
copy of the official template (`~/.claude/magang-tools/templates/pks_template.docx`).
Only the partner side (PIHAK KEDUA) and the date are variable — exactly the
fields highlighted yellow in the source template. PIHAK KESATU (UPI / KARIM
SURYADI / Direktur) and every pasal are fixed in the template; never ask for
them.
</workflow-note>

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

Config `pks_template_path` (null = bundled official template, the default).

## Step 2 — Collect partner (PIHAK KEDUA) information

Ask:
- Nama perusahaan/instansi lengkap (contoh: PT Fliptech Lentera Inspirasi Pertiwi)
- Nama penandatangan pihak perusahaan (contoh: LUQMAN SUNGKAR)
- Jabatan penandatangan (contoh: Kepala Engineering Konsumer PT Fliptech ...)
- Alamat lengkap perusahaan
- Nomor telepon (ketik "-" kalau tidak ada)
- Fax (ketik "-" kalau tidak ada)
- Email
- Wilayah/kota perusahaan (untuk frasa "di wilayah ___", contoh: Jakarta)

## Step 3 — Agreement date (terbilang + numeric)

The template spells the date out in words AND digits. Ask the student for
each part (manual, no auto-conversion):
- Hari (contoh: Senin)
- Tanggal terbilang (contoh: Satu — atau "Dua Puluh Tiga")
- Bulan (contoh: Juni)
- Tahun terbilang (contoh: Dua Ribu Dua Puluh Enam)
- Tanggal numerik dd-mm-yyyy (contoh: 01-06-2026)

## Step 4 — Generate DOCX

Build the data JSON with these exact keys, then write to a temp file
`/tmp/pks_data_[timestamp].json`:
```json
{
  "partner_org_upper": "<NAMA PERUSAHAAN HURUF KAPITAL>",
  "partner_org_sub": "",
  "partner_org": "<Nama Perusahaan Title Case>",
  "partner_rep_name": "<NAMA PENANDATANGAN>",
  "partner_rep_title": "<Jabatan penandatangan>",
  "partner_address": "<Alamat lengkap>",
  "partner_phone": "<Telepon>",
  "partner_fax": "<Fax>",
  "partner_email": "<Email>",
  "partner_region": "<Wilayah/kota>",
  "date_hari": "<Hari>",
  "date_tgl_word": "<Tanggal terbilang>",
  "date_bulan": "<Bulan>",
  "date_tahun_word": "<Tahun terbilang>",
  "date_numeric": "<dd-mm-yyyy>"
}
```
- `partner_org_upper` = all-caps (header). `partner_org` = title case (inline + signature). `partner_org_sub` = usually "" (only for a sub-unit line; leave blank).

Output path: `--output-dir` if given, else current dir. Filename
`PKS_[NamaPerusahaan_tanpa_spasi].docx`.

Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_pks.py \
    --data /tmp/pks_data_[timestamp].json \
    --output "[output_path]"
```
(The generator uses the bundled official template automatically; pass
`--template [pks_template_path]` only if config sets a custom one.)

Parse output JSON → final path (auto-versioned). Cleanup temp file.

## Step 5 — Summary

```
✅ PKS berhasil dibuat dari template resmi!
  File   : [output_path]
  Pihak 1: KARIM SURYADI (Direktur, UPI Cibiru) — tetap dari template
  Pihak 2: [rep_name] ([rep_title], [company])
  Tanggal: [hari], [date_numeric]

Next steps:
  1. Buka DOCX, sisipkan logo UPI + logo perusahaan secara manual
  2. Isi nomor dokumen kedua pihak (NOMOR: ___)
  3. Print 2 rangkap, tempel materai, tanda tangan kedua pihak
  4. Scan → simpan sebagai PKS_[NamaPerusahaan].pdf
```

</steps>
