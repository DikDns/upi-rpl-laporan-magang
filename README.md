# upi-rpl-laporan-magang

> **🧪 Status: Public Beta (`1.0.0-beta.1`)**
> Fungsional & sudah diuji pada pedoman RPL UPI Cibiru Versi ke-6, tapi
> **belum diuji menyeluruh lintas skenario pengguna**. Selalu **cek hasil
> DOCX manual** sebelum dikumpulkan. Lihat [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

Plugin Claude Code untuk mahasiswa **Rekayasa Perangkat Lunak UPI Cibiru**.
Bikin **logbook**, **laporan magang**, dan **PKS** otomatis — mengikuti
pedoman dan format dokumen kampus.

## Instalasi

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.ps1 | iex
```

Installer mendaftarkan plugin penuh (cache, marketplace, `settings.json`).
**Restart Claude Code** setelah instalasi → skill aktif.

## Skills

| Skill | Fungsi |
|-------|--------|
| `/rpl-magang:init` | Setup awal — parsing pedoman PDF, review, simpan config. **Jalankan sekali dulu.** |
| `/rpl-magang:logbook` | Logbook mingguan/dua mingguan (Catatan Harian & Kehadiran) → DOCX |
| `/rpl-magang:laporan` | Tulis laporan per bab + compile ke satu DOCX |
| `/rpl-magang:pks` | Isi PKS (Perjanjian Kerja Sama) dari template resmi |

### Yang dihasilkan laporan
- **Cover & Lembar Pengesahan** full-page sesuai pedoman (font 12/10/12/14, logo UPI)
- **Heading** konvensi kampus: BAB = 14pt bold center, sub-bab 12pt bold left (hitam, bukan biru bawaan Word)
- **Dokumentasi gambar** `![caption](path)` → embed + caption ber-nomor "Gambar X.Y"
- Kertas **A4**, margin 4/3/3/3, font dari config

## Cara Pakai

```
1. /rpl-magang:init                ← sekali, arahkan ke PDF pedoman
2. /rpl-magang:logbook             ← logbook tiap minggu
3. /rpl-magang:laporan cover       ← cover
4. /rpl-magang:laporan lembar-pengesahan
5. /rpl-magang:laporan bab1 … bab4 ← tulis tiap bab
6. /rpl-magang:laporan compile     ← ekspor DOCX lengkap
7. /rpl-magang:pks                 ← buat PKS
```

## Kebutuhan Sistem

- Python 3.9+ (`python-docx`, `pdfplumber`, `Pillow` — diinstall otomatis)
- Claude Code
- `curl` (macOS/Linux) atau PowerShell 5+ (Windows)

## Uninstall

```bash
./uninstall.sh
```

## Kontribusi & Lisensi

- Lapor bug / masukan: [Issues](https://github.com/DikDns/upi-rpl-laporan-magang/issues)
- Panduan: [CONTRIBUTING.md](CONTRIBUTING.md)
- Lisensi: [MIT](LICENSE)
- Perubahan: [CHANGELOG.md](CHANGELOG.md)

## Catatan

- Logo UPI ada di `assets/upi-logo.png`, otomatis dipakai di cover laporan.
- Config tersimpan di `~/.claude/magang-tools/config.json` — jalankan `/rpl-magang:init` ulang kalau pedoman berubah.
