# Changelog

Semua perubahan penting pada proyek ini dicatat di file ini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/),
dan proyek ini memakai [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Docs
- README: dokumentasikan skill `laporan-bab-*` yang digenerate otomatis saat `init`, skill `laporan-compile`, dan `penilaian-penyelia`; perbaiki contoh alur kerja yang masih memakai sintaks lama (`laporan bab1` / `laporan compile`); tambah catatan output ODT/PDF, sitasi APA, dan dependensi LibreOffice opsional.

## [1.0.0-rc.1] — 2026-06-12

Rilis perbaikan mesin compile laporan setelah uji pemakaian nyata (peran Test
Engineer). Fokus: **DAFTAR ISI/TABEL/GAMBAR yang beneran kebaca Word**, tata
letak A4 konsisten, sitasi APA, dan output multi-format.

### Added
- Skill `penilaian-penyelia`: generate the official Lembar Penilaian Penyelia DOCX (pedoman v6) — blank for hand-scoring or prefilled with auto-computed Jumlah & Rata-rata.
- `init` now extracts `penilaian_penyelia` indicators from the pedoman into config (with a pedoman-v6 default fallback for existing configs).
- **Output multi-format** via LibreOffice — `--also odt` (default) / `--also pdf` menghasilkan ODT/PDF di samping DOCX. Tahan path berisi spasi (convert lewat tempdir tanpa spasi).
- **Sitasi APA & Daftar Pustaka** — skill `laporan` Step 5: setiap klaim faktual butuh in-text `(Penulis, Tahun)` + entri `daftar-pustaka.md`; section `daftar-pustaka` otomatis hanging indent (APA-7). Bab skills sekarang mengingatkan klaim yang belum tersitasi.
- **Konvensi markdown baru** yang didukung engine: `_italic_`, caption tabel `Tabel: <judul>` (→ DAFTAR TABEL), dan blok tanda tangan `[SIGN] … [/SIGN]`. Didokumentasikan di `docs/KONVENSI_MARKDOWN.md`.

### Fixed
- **A4 + PORTRAIT di semua section.** Section break setelah cover sebelumnya ter-render Letter/landscape karena `sectPr` tanpa `pgSz`/`pgMar`; sekarang semua `doc.sections` dipaksa A4 portrait + margin dari config.
- **DAFTAR ISI/TABEL/GAMBAR tidak lagi kosong.** Heading kini memakai Word Heading styles (bukan paragraf bold biasa), front-matter title jadi Heading 1, field TOC well-formed (`fldChar separate` + placeholder), dan `updateFields=true` → Word/LibreOffice auto-update saat dibuka.
- **Judul bab "BAB I … IV"** dirender dua baris terpusat (Roman + judul) dalam satu Heading 1.
- **Italic `_..._`** kini ter-parse (sebelumnya tampil literal dengan underscore).
- **Caption gambar & tabel via field SEQ** (style "Caption", prefix per-bab "Gambar/Tabel B.N"), warna dipaksa hitam (sebelumnya angka jadi biru saat field di-update). DAFTAR TABEL/GAMBAR muncul hanya jika ada caption-nya.
- **Hanya section dikenal yang di-compile** (`^bab\d+$` + front/back-matter) — Logbook, PKS, lampiran milik penulis tidak ikut ter-compile otomatis.
- **Numbered list** dirender manual dengan hanging indent dan **restart per list** (dulu satu counter global bikin Bab IV mulai dari angka besar).
- **Paragraf justify**; **Daftar Pustaka** hanging indent (APA).
- **Lembar Pengesahan & blok tanda tangan** memakai tabel borderless (label | `:` | value) — titik dua sejajar di font proporsional.

## [1.0.0-beta.2] — 2026-06-01

Rilis perbaikan setelah uji pemakaian nyata (logbook Test Engineer, ~2 bulan
magang). Fokus: **bug tata letak tabel yang sistemik** + dukungan logbook
yang sesuai praktik (per-pekan, bullet, istilah teknis).

### Fixed
- **Lebar kolom tabel kini dihormati Word.** Jumlah lebar kolom logbook
  sebelumnya 17cm melebihi area cetak (A4 − margin kiri 4 − kanan 3 = 14cm),
  sehingga Word membuang lebar dan meratakan semua kolom (No/Tanggal ikut
  melebar, Uraian jadi sempit). Sekarang dipasang `tblLayout=fixed` +
  `tblGrid` eksplisit dan total lebar dibatasi ≤ area cetak.
  → audit `generate_laporan.py` (tabel Jadwal Kegiatan Bab II & Teknologi
  Bab III) untuk bug yang sama.
- **Titik dua blok identitas logbook kini sejajar.** Dulu memakai padding
  spasi `f"{label:<20}: "` pada font proporsional (Arial) → tidak lurus.
  Sekarang tabel borderless 3 kolom (label | `:` | value).
- **Blok tanda tangan logbook** dari 6 baris (4 baris kosong mubazir) → 3
  baris dengan satu baris tinggi (~3cm) untuk menempel gambar tanda tangan.

### Added
- **Logbook mode per-pekan** — satu baris = rentang tanggal satu pekan
  (`weeks:[{label, periode, entries}]`); hari libur / tanggal merah otomatis
  terlewati (hanya hari kerja yang ada yang ditulis).
- **Bullet points per hari** (`items:[...]`) untuk hari dengan banyak
  aktivitas, menggantikan satu blok teks.
- **Rendering inline** di dalam sel: `*italic*` untuk istilah teknis/asing
  dan `` `code` `` (monospace) untuk perintah/berkas.
- **Enrich dari sumber data** — ekstraksi anotasi hyperlink dari PDF logbook,
  lalu fetch detail via ClickUp (MCP) dan GitLab (`glab`) untuk menyusun
  uraian otomatis (judul Merge Request, ID bug/task, status).
- **Cache identitas mahasiswa** di `config.json` (diisi sekali saat `init`),
  dipakai ulang lintas skill `laporan` / `logbook` / `pks` tanpa tanya ulang.

### Changed
- `generate_logbook.py` di-refactor: render tabel & blok tanda tangan
  dipindah ke helper. **Backward-compatible** — input `entries` flat lama
  (string `uraian_aktivitas`) tetap jalan.

## [1.0.0-beta.1] — 2026-05-31

Rilis **public beta** pertama. Empat skill lengkap, sudah diuji pada
pedoman RPL UPI Cibiru "Versi ke-6 MBKM/P3NK", **belum diuji lintas
skenario pengguna** (lihat `KNOWN_LIMITATIONS.md`).

### Added
- **`/rpl-magang:init`** — parsing pedoman PDF (struktur bab, formatting,
  komponen penilaian, template logbook), review interaktif, simpan ke
  `~/.claude/magang-tools/config.json`.
  - Ekstraksi struktur dibatasi pada blok "Bagian Isi" resmi → bab/section
    bersih tanpa kontaminasi nomor dari list lain.
  - `rpl_emphasis` — pengingat menonjolkan sisi RPL/SE di tiap bab.
  - `sections_flexible` — section bab III dianggap saran, bisa disesuaikan.
  - `page_size: A4` default.
- **`/rpl-magang:logbook`** — logbook mingguan/dua mingguan (Catatan Harian
  & Kehadiran), mode single/batch/import, ekspor DOCX A4.
- **`/rpl-magang:laporan`** — tulis laporan per bab + compile ke satu DOCX:
  - Cover & Lembar Pengesahan full-page sesuai pedoman (ukuran font
    12/10/12/14, logo UPI, blok institusi).
  - Heading mengikuti konvensi kampus (H1 14pt center, H2/H3 12pt left,
    hitam, bukan style biru bawaan Word).
  - Dokumentasi gambar `![caption](path)` → embed 14pt + caption
    ber-nomor otomatis "Gambar X.Y".
  - KATA PENGANTAR / DAFTAR ISI / DAFTAR PUSTAKA / LAMPIRAN sebagai H1.
  - Ukuran kertas A4, margin dari config (4/3/3/3).
- **`/rpl-magang:pks`** — isi placeholder template PKS resmi (bukan
  generate dari nol); PIHAK KESATU (UPI) + semua pasal tetap verbatim,
  hanya PIHAK KEDUA (mitra) + tanggal yang diisi.
- Installer `curl | bash` (macOS/Linux) & `irm | iex` (Windows) yang
  mendaftarkan plugin penuh: cache, marketplace, `known_marketplaces.json`,
  `settings.json` (`enabledPlugins` + `extraKnownMarketplaces`).

[1.0.0-rc.1]: https://github.com/DikDns/upi-rpl-laporan-magang/releases/tag/v1.0.0-rc.1
[1.0.0-beta.2]: https://github.com/DikDns/upi-rpl-laporan-magang/releases/tag/v1.0.0-beta.2
[1.0.0-beta.1]: https://github.com/DikDns/upi-rpl-laporan-magang/releases/tag/v1.0.0-beta.1
