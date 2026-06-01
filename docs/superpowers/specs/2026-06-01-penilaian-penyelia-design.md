# Design — Skill `penilaian-penyelia`

**Date:** 2026-06-01
**Status:** Approved
**Scope:** Add a new rpl-magang skill that generates the official "Lembar Penilaian Penyelia" DOCX, sourced from pedoman v6.

## Problem

The rpl-magang plugin generates logbook, laporan, and PKS, but not the supervisor
assessment form ("Lembar Penilaian Penyelia") that the pedoman requires as a
lampiran. Students currently format this by hand. The form layout is fixed by the
pedoman (page 11 of "Versi ke-6 Pedoman Laporan MBKM atau P3NK"), so it should be
generated to match — driven by config extracted during `/rpl-magang:init`.

## Source of truth (pedoman v6, page 11)

Form "Lampiran Form Lembar Penilaian Penyelia":

- Letterhead placeholder: `----- KOP SURAT INSTITUSI MITRA ---------`
- Title: `PENILAIAN PELAKSANAAN KEGIATAN MBKM PROGRAM MSIB / P3NK (MAGANG MANDIRI)`
- Identity fields: Nama Penyelia, Nama INSTITUSI MITRA, Nama Mahasiswa,
  Nomor Induk Mahasiswa, Waktu Pelaksanaan
- Intro paragraph (verbatim): "Dengan mempertimbangkan segala aspek, baik dari
  segi bobot pekerjaan maupun pelaksanaan kegiatan MBKM Program MSIB / P3NK
  (Magang Mandiri), maka kami memutuskan bahwa yang bersangkutan telah
  menyelesaikan kewajibannya, sebagaimana terinci dalam indikator penilaian
  sebagai berikut:"
- Table `No. | Indikator Penilaian | Nilai*)` with 10 indicators + `Jumlah` row + `Rata-rata` row:
  1. Pemahaman terhadap tugas dan tanggung jawab
  2. Penguasaan konsep dan teori yang relevan
  3. Kemampuan dalam pemrograman / teknis
  4. Penggunaan teknologi, tools, dan framework
  5. Kualitas hasil kerja
  6. Kemampuan analisis, pemecahan masalah & inisiatif
  7. Komunikasi dan kolaborasi dalam tim
  8. Manajemen waktu dan ketepatan penyelesaian tugas
  9. Adaptasi terhadap lingkungan kerja dan perubahan
  10. Etika, sikap profesional, dan tanggung jawab
- Footnotes: `*) Skala/Rentang penilaian Penyelia 0 – 100.` and
  `**) Jika sudah ada form dari intansi, form penilaian ini tidak berlaku.`
- Signature: `Tempat, tanggal, bulan, tahun` / `Penyelia,` / name line /
  `Tandatangan, Nama, Posisi, dan di Stempel`

This form is distinct from config's existing `assessment_criteria` (5 general
aspek). It gets its own config key.

## Design decisions

- **Fill mode:** blank by default (printed → supervisor fills by hand); optional
  prefill where the student supplies scores and the generator auto-computes
  `Jumlah` (sum) and `Rata-rata` (sum / 10).
- **Indicator source:** extracted at init into a new config key
  `penilaian_penyelia`, with a bundled pedoman-v6 default fallback so existing
  configs and parse failures still work — no forced re-init.
- **Skill name:** `penilaian-penyelia` (`/rpl-magang:penilaian-penyelia`).

## Components

### 1. `scripts/generate_penilaian.py` (new)

Build-from-scratch DOCX, mirroring `generate_logbook.py` conventions
(`load_config`, `versioned_path`, `set_cell_border`, `set_fixed_layout`,
`add_identity`-style aligned label table, A4 + margins/font from
`config.formatting`).

Sections in order:
1. KOP placeholder paragraph: `[ KOP SURAT INSTITUSI MITRA ]`, centered, italic,
   grey — student inserts real letterhead later (same manual pattern as PKS logo).
2. Title (bold, centered).
3. Identity block (borderless `label | : | value` table): Nama Penyelia, Nama
   Institusi Mitra, Nama Mahasiswa, Nomor Induk Mahasiswa, Waktu Pelaksanaan.
4. Intro paragraph (verbatim, justified).
5. Bordered table `No. | Indikator Penilaian | Nilai*)`:
   - 10 indicator rows from `config.penilaian_penyelia.indicators` (fallback to
     bundled default).
   - `Jumlah` row, `Rata-rata` row.
   - Blank Nilai cells by default. If `data.nilai` provided, fill matching
     indices. Jumlah = sum of provided scores. Rata-rata = Jumlah / 10 (fixed
     divisor — the pedoman form has exactly 10 indicators), rounded to 2 decimals.
     Prefill is intended to be all 10; partial prefill still divides by 10.
   - Column widths sum to printable width (A4 21cm − left − right). Suggested
     `No.` 1.2cm, `Indikator` ~10.8cm, `Nilai` 2.0cm (recompute from actual
     margins like logbook does).
6. Footnotes (small font): scale note + "jika sudah ada form dari instansi" note,
   from `config.penilaian_penyelia` (`scale`, `note`) with verbatim defaults.
7. Signature block: `Tempat, tanggal` line (from data), `Penyelia,`, tall row for
   ttd image, name line, caption `Tandatangan, Nama, Posisi, dan di Stempel`.

Data JSON keys:
```json
{
  "nama_penyelia": "",
  "nama_institusi": "",
  "nama_mahasiswa": "",
  "nim": "",
  "waktu_pelaksanaan": "",
  "tempat_tanggal": "",
  "posisi_penyelia": "",
  "nilai": { "1": 85, "2": 90 }
}
```
`nilai` optional — omit or empty object → blank form (Jumlah/Rata-rata blank too).
Missing indices → blank cell; Jumlah/Rata-rata computed as above (divisor fixed at 10). CLI: `--data <json> --output <docx>` → prints `{"success", "output"}`.

### 2. `scripts/init_pedoman.py` (modify)

Add `extract_penilaian_penyelia(full_text) -> dict`:
- Locate the "Lembar Penilaian Penyelia" / "Indikator Penilaian" region.
- Parse numbered indicators, rejoining line-wrapped titles (e.g. "...tanggung\njawab"
  → one entry). Stop at `Jumlah` / `Rata-rata` / footnote markers.
- Return `{ "title", "scale": "0 – 100", "indicators": [...], "note": "..." }`.
- If parsing yields ≠ a sane count (e.g. < 5), return the bundled pedoman-v6
  default (the 10 indicators above).
- Add `"penilaian_penyelia": extract_penilaian_penyelia(full_text)` to the config
  dict in `main()`.

### 3. `skills/penilaian-penyelia/SKILL.md` (new)

Frontmatter mirrors `pks`/`logbook` (name, description, argument-hint
`[--output-dir /path]`, allowed-tools Read/Write/Bash/AskUserQuestion).

Steps:
1. Check `~/.claude/magang-tools/config.json` exists → else "Jalankan
   /rpl-magang:init dulu." Stop.
2. Collect identity. Use `config.student_identity` defaults (nama, nim, mitra→
   institusi, penyelia) — confirm, don't re-ask from zero. Ask: Waktu Pelaksanaan,
   Posisi Penyelia, Tempat & tanggal (e.g. "Bandung, 1 Juni 2026").
3. Ask prefill? If yes → collect 10 nilai (0–100); else blank form.
4. Write `/tmp/penilaian_data_[ts].json`, run generator, output
   `Penilaian_Penyelia_[NamaMahasiswa_tanpa_spasi].docx` (`--output-dir` or cwd).
   Cleanup temp.
5. Summary + reminders: cetak di atas KOP surat institusi mitra, isi nilai bila
   kosong, ttd + posisi + stempel penyelia. Note: kalau instansi sudah punya form
   sendiri, form ini tidak berlaku.

### 4. Docs (modify)

- `README.md`: add `/rpl-magang:penilaian-penyelia` to the skills/commands listing
  alongside logbook/laporan/pks, matching existing style.
- `CHANGELOG.md`: add entry under Unreleased/next beta — new penilaian-penyelia
  skill + init extracts `penilaian_penyelia`.

## Deployment

No manifest edits. `install.sh` globs `scripts/*.py` → `~/.claude/magang-tools/scripts/`
and skills auto-discover from `skills/`. Existing users re-run `install.sh` (or
copy the new script) to pick up `generate_penilaian.py`; the skill works against
existing config via the fallback, and a fresh `/rpl-magang:init` adds the
`penilaian_penyelia` key.

## Testing

- Generate a blank form → open DOCX, verify 10 indicators + Jumlah + Rata-rata,
  borders, KOP placeholder, footnotes, signature, A4/margins.
- Generate prefilled (sample scores) → verify Jumlah = sum, Rata-rata = sum/10.
- Run `init_pedoman.py --pdf <pedoman v6>` → assert `penilaian_penyelia.indicators`
  has the 10 expected titles, none truncated mid-word.
- Run init against a non-pedoman / unparsable PDF path → assert fallback default
  returned, no crash.

## Out of scope

- No changes to existing `assessment_criteria` semantics.
- No automatic letterhead/logo insertion (manual, like PKS).
- No PDF export (DOCX only, matching sibling skills).
