<div align="center">

# rpl-magang

**Magang. Tulis. Beres.**

**Plugin Claude Code untuk mahasiswa Rekayasa Perangkat Lunak UPI Cibiru — generate logbook, laporan magang, dan PKS yang mengikuti pedoman dan format dokumen kampus.**

**Berhenti nyalin-tempel placeholder dan ngerapihin format DOCX manual.** Arahkan ke PDF pedoman sekali, sisanya skill yang urus — struktur bab, cover, lembar pengesahan, heading, sampai PKS dari template resmi.

![Status](https://img.shields.io/badge/status-public%20beta-orange) ![Versi](https://img.shields.io/badge/versi-1.0.0--beta.1-blue) ![Lisensi](https://img.shields.io/badge/lisensi-MIT-green)

</div>

---

## Instalasi

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.ps1 | iex
```

**Skill ga muncul?** Restart Claude Code setelah install. Plugin terpasang di `~/.claude/plugins/cache/rpl-magang/` dan terdaftar otomatis di `settings.json`.

> 🧪 **Public beta** — sudah jalan & teruji pada pedoman RPL UPI Cibiru Versi ke-6, tapi belum diuji menyeluruh lintas skenario. **Selalu cek hasil DOCX manual** sebelum dikumpulkan. Lihat [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

---

## Skills

Empat skill. Tiap satu ngerjain satu hal.

| Skill | Fungsi |
|-------|--------|
| `/rpl-magang:init` | **Jalankan sekali dulu.** Parsing pedoman PDF → struktur bab, formatting, komponen penilaian. Review, lalu simpan ke config. |
| `/rpl-magang:logbook` | Logbook mingguan/dua mingguan (Catatan Harian & Kehadiran) → DOCX. Mode single, batch, atau import. |
| `/rpl-magang:laporan` | Tulis laporan per bab, lalu `compile` jadi satu DOCX lengkap. |
| `/rpl-magang:pks` | Isi PKS (Perjanjian Kerja Sama) dari template resmi — hanya bagian mitra yang diisi. |

Alurnya: `init` sekali → `logbook` tiap minggu → `laporan` per bab → `compile` → `pks`.

---

## Cara Kerja

**Pedoman jadi sumber kebenaran.** `init` baca PDF pedoman kamu, ekstrak struktur bab (dari blok "Bagian Isi" resmi), aturan format (font, margin, spasi, kutipan), dan komponen penilaian — lalu kamu review sebelum disimpan. Semua skill lain baca config ini.

**Skill nuntun, script yang generate.** Tiap skill adalah alur percakapan: dia nanya yang perlu, kamu jawab pakai bahasa bebas, lalu script Python (`python-docx`) yang nyusun DOCX final sesuai format kampus.

**Laporan yang dihasilkan:**
- **Cover & Lembar Pengesahan** full-page sesuai pedoman (ukuran font 12/10/12/14, logo UPI, blok institusi di bawah)
- **Heading** konvensi kampus — BAB 14pt bold center, sub-bab 12pt bold left, hitam (bukan style biru bawaan Word)
- **Dokumentasi gambar** `![keterangan](path)` → embed otomatis + caption ber-nomor "Gambar X.Y"
- **KATA PENGANTAR / DAFTAR ISI / DAFTAR PUSTAKA / LAMPIRAN** sebagai heading bab
- Kertas **A4**, margin & font dari config

**PKS yang mirror cara manual.** Bukan generate dari nol — script isi placeholder di **template resmi** (turunan "Cth. PKS atau MoU.docx"). Semua pasal dan PIHAK KESATU (UPI) tetap verbatim; cuma PIHAK KEDUA (mitra) + tanggal yang diisi. Persis seperti ganti bagian yang di-highlight kuning, tapi otomatis.

---

## Kenapa Begini

Laporan magang kampus itu format-heavy: ukuran font per baris, struktur bab baku, cover full-page, PKS legal yang ga boleh berubah pasalnya. Ngerjain manual = rawan typo, format geser, dan lupa bagian wajib (mis. Lembar Pengesahan).

Plugin ini ngotomatiskan bagian mekanisnya — **mahasiswa fokus ke isi (yang ditonjolkan: sisi RPL/software engineering)**, bukan ke rapihin DOCX.

---

## Contoh Pakai

```
1. /rpl-magang:init                  # sekali, arahkan ke PDF pedoman
2. /rpl-magang:logbook               # logbook tiap minggu
3. /rpl-magang:laporan cover
4. /rpl-magang:laporan lembar-pengesahan
5. /rpl-magang:laporan bab1 … bab4   # tulis tiap bab
6. /rpl-magang:laporan compile       # ekspor DOCX lengkap
7. /rpl-magang:pks                   # buat PKS
```

---

## Kebutuhan Sistem

- **Python 3.9+** — `python-docx`, `pdfplumber`, `Pillow` (diinstall otomatis di venv)
- **Claude Code**
- `curl` (macOS/Linux) atau **PowerShell 5+** (Windows)

---

## Dokumentasi

| Dok | Isinya |
|-----|--------|
| [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) | Batasan beta — apa yang belum diuji, hati-hati di mana |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cara lapor bug, setup development, alur kerja |
| [CHANGELOG.md](CHANGELOG.md) | Perubahan tiap rilis |

---

## Uninstall

```bash
./uninstall.sh
```

---

## Lisensi

[MIT](LICENSE).

<div align="center">

Dibuat untuk mahasiswa RPL UPI Cibiru.
Lapor bug & masukan di [Issues](https://github.com/DikDns/upi-rpl-laporan-magang/issues).

</div>
