# Changelog

Semua perubahan penting pada proyek ini dicatat di file ini.
Format mengikuti [Keep a Changelog](https://keepachangelog.com/),
dan proyek ini memakai [Semantic Versioning](https://semver.org/).

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

[1.0.0-beta.1]: https://github.com/DikDns/upi-rpl-laporan-magang/releases/tag/v1.0.0-beta.1
