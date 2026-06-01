---
name: init
description: "One-time setup — parse pedoman PDF, review extracted config, and save for use by other rpl-magang skills"
argument-hint: "[--pdf /path/to/pedoman.pdf]"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Run once to set up rpl-magang. Parse the user's pedoman PDF, show the extracted config for review and correction, then save to ~/.claude/magang-tools/config.json. All other rpl-magang skills depend on this config.
</objective>

<constants>
TOOLS_DIR   = ~/.claude/magang-tools
CONFIG_PATH = ~/.claude/magang-tools/config.json
PYTHON      = ~/.claude/magang-tools/venv/bin/python
INIT_SCRIPT = ~/.claude/magang-tools/scripts/init_pedoman.py
</constants>

<steps>

## Step 1 — Check existing config

Run:
```bash
test -f ~/.claude/magang-tools/config.json && echo "exists" || echo "not_found"
```

If config exists → show warning: "Config sudah ada dari sebelumnya. Re-init akan menimpa konfigurasi yang lama." Ask:
- "Lanjut re-init?" → if No, stop.

## Step 2 — Collect pedoman PDF path

If `$ARGUMENTS` contains `--pdf`, extract path from there.
Otherwise ask:

> "Berikan path ke file pedoman PDF kamu (contoh: ~/Downloads/Pedoman_MBKM.pdf):"

Validate the path exists before continuing:
```bash
test -f "[PATH]" && echo "ok" || echo "not_found"
```

If not found → ask again.

## Step 3 — Parse pedoman PDF

Run:
```bash
~/.claude/magang-tools/venv/bin/python ~/.claude/magang-tools/scripts/init_pedoman.py --pdf "[PDF_PATH]"
```

Parse the JSON output.

**If exit code 2 (pdf_parse_failed)** → go to Step 3b (manual fallback).

**If exit code 0** → go to Step 4 (review).

## Step 3b — Manual config fallback

Tell user: "PDF tidak bisa dibaca otomatis. Gw akan tanya manual."

Ask the following (can batch into one AskUserQuestion call or multiple):
- Program studi (default: Rekayasa Perangkat Lunak)
- Nama kampus (default: Kampus UPI di Cibiru)
- Font laporan (default: Arial)
- Ukuran font body (default: 11pt)
- Spasi baris (default: 1.5)
- Margin kiri/atas/bawah/kanan dalam cm (default: 4/3/3/3)
- Style kutipan (default: APA)
- Struktur Bab I (sub-sections, comma-separated)
- Struktur Bab II (sub-sections)
- Struktur Bab III (sub-sections)
- Struktur Bab IV (sub-sections)
- Komponen penilaian (comma-separated)

Build config dict from answers. Skip Step 4, go to Step 5.

## Step 4 — Show extracted config for review

Display extracted info in a readable format. Example:

```
📋 Hasil ekstraksi dari pedoman:

FORMATTING:
  Font         : Arial 11pt
  Spasi        : 1.5
  Margin       : 4cm kiri, 3cm atas/bawah/kanan
  Kutipan      : APA

STRUKTUR LAPORAN:
  Bab I   : Pendahuluan (1.1 Latar Belakang, 1.2 Manfaat & Tujuan, ...)
  Bab II  : Profil Institusi Mitra (2.1, 2.2, ...)
  Bab III : Pelaksanaan Kegiatan (3.1, 3.2, ...)
  Bab IV  : Kesimpulan dan Saran (4.1, 4.2)

KOMPONEN PENILAIAN:
  1. Aspek kemampuan kompetensi dan ketrampilan
  2. Aspek personal dan sosial
  3. ...
```

**Sanity-check the extracted structure before showing it** (safety net on top of the extractor):
- Duplicate section numbers within a bab (e.g. two `3.1`) → keep the one matching the bab's real outline, drop the stray.
- A section whose chapter digit ≠ its bab (e.g. a `4.1 Substansi` sitting in Bab IV alongside the real `4.1 Kesimpulan`) → drop the off-topic one; the real Bab IV is "Kesimpulan dan Saran".
- Titles cut mid-word or with stray characters → clean them.
Flag anything you fix so the student can confirm: "Gw rapihin [X] karena [alasan] — bener?"

Then ask: "Ada yang perlu dikoreksi? Kalau ada, sebutkan field mana dan nilai yang benar. Kalau sudah oke ketik 'lanjut'."

If user provides corrections → apply them to the config dict.
If user types 'lanjut' or equivalent → proceed.

## Step 5 — Ask for custom PKS template (optional)

Ask: "Punya template PKS DOCX sendiri? Kalau ada, berikan path-nya. Kalau tidak, skip (Enter)."

If path provided → validate it exists → set `pks_template_path` in config.
If skipped → `pks_template_path` remains null (use built-in).

## Step 5b — Identitas mahasiswa (opsional)

Ask (boleh skip dengan Enter): "Mau simpan identitas biar nggak ditanya ulang
tiap skill? (boleh skip)"
- Nama Mahasiswa (lengkap)
- NIM
- Nama Mitra (perusahaan/instansi)
- Nama Penyelia (supervisor di tempat magang)

Bila diisi, simpan ke config sebagai `student_identity`:
```json
{ "student_identity": { "nama": "...", "nim": "...", "mitra": "...", "penyelia": "..." } }
```
Skill `laporan` / `logbook` / `pks` membaca ini dan hanya minta konfirmasi,
tidak tanya ulang. Bila skip, `student_identity` tidak ditulis (skill akan
menanyakannya saat dibutuhkan, lalu menyimpannya balik).

## Step 5c — Konfirmasi konvensi penamaan file (opsional)

Tampilkan template nama file default dari config dan tanyakan apakah ada yang mau diubah:

```
📁 Konvensi penamaan file P3NK (dari panduan):

  form_konversi    : Form_Mk_Konversi_MBKM_{nama_mhs}.xlsx
  loa              : LoA_{nama_mhs}.pdf
  logbook          : Logbook_{nama_mhs}.pdf
  laporan          : Laporan_MBKM_{nama_mhs}.pdf
  transkrip_nilai  : Transkrip_Nilai_{nama_mhs}.pdf
  pks              : PKS_{nama_perusahaan}.pdf
  presentasi       : presentasi_{nama_mhs}.mp4
  sertifikat       : Sertifikat_{nama_kegiatan}_{nama_mhs}.pdf
```

Tanya: "Ada template nama file yang mau diubah? Kalau sudah sesuai, ketik 'lanjut'."

Jika user ubah salah satu → update key yang relevan di `config["file_naming"]`.
Jika skip/lanjut → biarkan default.

## Step 6 — Save config

Write config to `~/.claude/magang-tools/config.json`.

```bash
mkdir -p ~/.claude/magang-tools
```

Use the Write tool to write the final config JSON.

## Step 8 — Generate per-bab skills

Run:
```bash
~/.claude/magang-tools/venv/bin/python \
  ~/.claude/magang-tools/scripts/generate_bab_skills.py \
  --config ~/.claude/magang-tools/config.json \
  --output-dir ~/.claude/magang-tools/generated-skills
```

Parse JSON output. If error → show error, continue (skills can be regenerated later).

Sync generated skills to plugin cache:
```bash
CACHE=$(ls -d ~/.claude/plugins/cache/rpl-magang/rpl-magang/*/skills 2>/dev/null | sort -V | tail -1)
if [ -n "$CACHE" ]; then
  for skill_dir in ~/.claude/magang-tools/generated-skills/laporan-bab-*/; do
    [ -d "$skill_dir" ] && cp -r "$skill_dir" "$CACHE/"
  done
fi
```

Show which skills were generated:
```
🔧 Skills yang di-generate dari pedoman kamu:
  /rpl-magang:laporan-bab-1  — BAB I [title from config]
  /rpl-magang:laporan-bab-2  — BAB II [title from config]
  /rpl-magang:laporan-bab-3  — BAB III [title from config]
  /rpl-magang:laporan-bab-4  — BAB IV [title from config]
```

## Step 7 — Confirm

Show:
```
✅ Setup selesai! Config disimpan di ~/.claude/magang-tools/config.json

Skills siap digunakan:
  /rpl-magang:laporan             — cover, lembar pengesahan, kata pengantar
  /rpl-magang:laporan-compile     — compile semua section jadi DOCX
  /rpl-magang:logbook             — buat logbook mingguan
  /rpl-magang:pks                 — buat PKS
  /rpl-magang:penilaian-penyelia  — buat lembar penilaian penyelia

⚠️  RESTART CLAUDE CODE untuk mengaktifkan skill bab yang baru di-generate:
  /rpl-magang:laporan-bab-1, laporan-bab-2, laporan-bab-3, laporan-bab-4
```

</steps>
