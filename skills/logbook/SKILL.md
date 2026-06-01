---
name: logbook
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
LINKS_SCRIPT   = ~/.claude/magang-tools/scripts/extract_pdf_links.py
</constants>

<data-format>
`generate_logbook.py` menerima dua bentuk JSON (backward-compatible):

1. **Flat** (lama): `{..., entries:[{tanggal, uraian_aktivitas}]}` → satu tabel,
   satu baris per hari, satu blok tanda tangan di akhir.
2. **Per-pekan**: `{..., weeks:[{label, periode, entries:[{tanggal, items:[...]}]}]}`
   → satu tabel + satu tanda tangan per pekan, ganti halaman antar pekan.

Catatan render di dalam sel Uraian:
- `items` (list) → tiap item jadi **bullet point** (untuk hari dengan banyak
  aktivitas). String `uraian_aktivitas` tetap dipakai bila ada.
- `*teks*` → *italic* (istilah teknis/asing), `` `teks` `` → monospace code
  (perintah/berkas). Nama brand/ID (ClickUp IR-xxxx, dsb) biarkan biasa.

Pilihan bentuk ikut permintaan mahasiswa: bisa "1 baris = 1 hari" atau
"1 baris = 1 pekan dengan rentang tanggal + bullet". Tanyakan bila ambigu.
</data-format>

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

**Jika file PDF (mis. export ClickUp/Notion/Docs):** teksnya bisa berupa
gambar — baca per halaman (Read dengan `pages`) untuk isi, lalu **ekstrak
hyperlink** yang tersemat:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/extract_pdf_links.py \
    --pdf "[path.pdf]"
```

**Enrich (opsional, kalau ada link + tooling):** untuk tiap link, ambil detail
agar uraian akurat:
- `clickup` → ClickUp MCP `clickup_get_task` (custom id seperti IR-9633) untuk
  judul/ID/status task atau bug.
- `gitlab` → `glab mr view <iid> -R <project-path>` untuk judul/state Merge
  Request.
- `google` → catat sebagai dokumen pendukung (judul saja).

Gabungkan hasilnya ke uraian (judul MR, ID bug, status) sehingga aktivitas
harian deskriptif dan terverifikasi. Lewati enrich bila MCP/`glab` tak tersedia
atau user tak mengizinkan akses.

Show extracted entries to user for review: "Ini yang berhasil gw parse dari file kamu:"
Ask if there's anything to correct or add.

### Step 2c — Batch mode

Ask: "Berapa minggu yang mau dibuat sekaligus?" (e.g. 4)
Then for each week, ask for the date range.
Activities will be collected per week in Step 4.

## Step 3 — Collect student identity

Read `student_identity` from `config.json`. If present, confirm:
"Pakai data ini? Nama: [X], NIM: [Y], Mitra: [Z], Penyelia: [W]"

If absent or different → ask:
- Nama Mahasiswa (lengkap)
- NIM
- Nama Mitra (nama lengkap perusahaan/instansi)
- Nama Penyelia (nama supervisor di perusahaan)

After collecting (or correcting), **persist back** to
`config.json` under `student_identity` so `laporan` / `logbook` / `pks` reuse
it without re-asking:
```json
{ "student_identity": { "nama": "...", "nim": "...", "mitra": "...", "penyelia": "..." } }
```

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
