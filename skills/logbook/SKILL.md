---
name: rpl-magang:logbook
description: "Generate weekly/biweekly logbook (Catatan Harian & Kehadiran) for MBKM/P3NK — supports single week, batch, and import from existing files"
argument-hint: "[--week N] [--batch] [--import /path/to/file] [--output-dir /path]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Generate a Catatan Harian & Kehadiran Peserta logbook following the UPI template. Save as .md draft first, then export to .docx. Supports single week, batch weeks, and converting existing free-format notes to the template.
</objective>

<constants>
CONFIG_PATH    = ~/.claude/magang-tools/config.json
PYTHON         = ~/.claude/magang-tools/venv/bin/python
LOGBOOK_SCRIPT = ~/.claude/magang-tools/scripts/generate_logbook.py
</constants>

<steps>

## Step 1 — Check config

```bash
test -f ~/.claude/magang-tools/config.json && echo "ok" || echo "missing"
```

If missing → tell user: "Jalankan /rpl-magang:init dulu sebelum membuat logbook." Stop.

Load config to get logbook template structure and formatting.

## Step 2 — Determine mode

Check `$ARGUMENTS`:
- `--import /path` → Import mode (Step 2b)
- `--batch`        → Batch mode (Step 2c)
- default          → Single week mode (Step 2a)

### Step 2a — Single week mode

Ask (can batch these questions):
- Nomor minggu (contoh: 1, 2, 3...)
- Tanggal mulai minggu ini (contoh: 2 Juni 2025)
- Tanggal selesai minggu ini (contoh: 6 Juni 2025)

### Step 2b — Import mode

Tell user: "Gw akan konversi file kamu ke format template UPI."

Read the file at the provided path.

Analyze its content and extract:
- Tanggal per entry
- Uraian aktivitas per entry
- Nama penyelia (if found)

Show extracted entries to user for review: "Ini yang berhasil gw parse dari file kamu:"
Ask if there's anything to correct or add.

### Step 2c — Batch mode

Ask: "Berapa minggu yang mau dibuat sekaligus?" (e.g. 4)
Then for each week, ask for the date range.
Activities will be collected per week in Step 4.

## Step 3 — Collect student identity

Check if config already has student identity cached. If yes, confirm:
"Pakai data ini? Nama: [X], NIM: [Y], Mitra: [Z], Penyelia: [W]"

If no or different → ask:
- Nama Mahasiswa (lengkap)
- NIM
- Nama Mitra (default: PT Fliptech Lentera Inspirasi Pertiwi)
- Nama Penyelia (nama supervisor di perusahaan)

## Step 4 — Collect daily activities

For each working day in the week(s), ask for:
- Tanggal (format: Senin, 2 Juni 2025)
- Uraian Aktivitas

User can provide activities in any form — informal notes, English, bullet points. Always expand and rewrite as formal Bahasa Indonesia sentences (2–3 kalimat per entry). Example:

Input: "fixing bug payment timeout"
Output: "Melakukan identifikasi dan perbaikan bug pada modul payment service yang menyebabkan kegagalan transaksi akibat kondisi timeout. Perbaikan diverifikasi melalui pengujian unit test dan dinyatakan berhasil."

If a day was off (holiday, izin) → include entry with note: "Tidak masuk — [alasan]"

## Step 5 — Save .md draft

Determine output directory:
- If `--output-dir` in args → use that
- Default → current working directory

Draft filename: `Logbook_[NamaMhs]_Minggu[N].md` (spaces → underscore)

Write .md draft with this structure:
```markdown
# CATATAN HARIAN & KEHADIRAN PESERTA
## KEGIATAN MBKM KEGIATAN PROGRAM MSIB / P3NK (MAGANG MANDIRI) PADA MITRA

**Nama Mahasiswa :** [nama]
**NIM             :** [nim]
**Nama Mitra      :** [mitra]
**Nama Penyelia   :** [penyelia]

| No. | Tanggal | Uraian Aktivitas | Paraf Penyelia |
|-----|---------|-----------------|----------------|
| 1   | [tanggal] | [aktivitas] | |
| 2   | ...     | ...             | |

---

Peserta,                              Penyelia,



[Nama Mahasiswa]                      [Nama Penyelia]
NIM: [NIM]
```

Tell user: "Draft disimpan di [path]. Cek dulu sebelum export ke DOCX."

## Step 6 — Export to DOCX

Ask: "Mau langsung export ke DOCX sekarang?"

If Yes:
1. Build data JSON from collected info
2. Write to temp file: `/tmp/logbook_data_[week].json`
3. Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/generate_logbook.py \
    --data /tmp/logbook_data_[week].json \
    --output "[output_dir]/Logbook_[NamaMhs]_Minggu[N].docx"
```
4. Parse output JSON → get final path (auto-versioned if file existed)
5. Tell user: "DOCX berhasil dibuat: [path]"
6. Cleanup temp file.

If No → tell user how to re-run later: "/rpl-magang:logbook --week [N]"

## Step 7 — Summary

Show:
```
✅ Logbook Minggu [N] selesai!
  Draft : [path].md
  DOCX  : [path].docx (atau belum di-export)
  Entries: [N] hari

Next: cetak DOCX, minta tanda tangan penyelia di kolom Paraf, scan jadi PDF.
Nama file final: Logbook_[NamaMhs].pdf
```

</steps>
