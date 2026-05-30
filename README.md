# upi-rpl-laporan-magang

Plugin Claude Code untuk mahasiswa RPL UPI Cibiru. Membuat logbook, laporan magang, dan PKS secara otomatis berdasarkan pedoman yang berlaku.

## Instalasi

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/dikdns/upi-rpl-laporan-magang/main/install.ps1 | iex
```

Restart Claude Code setelah instalasi.

## Skills

| Skill | Fungsi |
|-------|--------|
| `/rpl-magang:init` | Setup awal — parsing pedoman PDF dan simpan konfigurasi |
| `/rpl-magang:logbook` | Buat logbook mingguan/dua mingguan (Catatan Harian & Kehadiran) |
| `/rpl-magang:laporan` | Tulis laporan magang per bab, kompilasi ke DOCX |
| `/rpl-magang:pks` | Buat PKS (Perjanjian Kerja Sama) dalam format DOCX |

## Cara Pakai

```
1. /rpl-magang:init              ← jalankan sekali, arahkan ke PDF pedoman
2. /rpl-magang:logbook           ← buat logbook setiap minggu
3. /rpl-magang:laporan bab1      ← tulis Bab I
4. /rpl-magang:laporan bab2      ← tulis Bab II
   ...
5. /rpl-magang:laporan compile   ← ekspor DOCX lengkap
6. /rpl-magang:pks               ← buat PKS
```

## Kebutuhan Sistem

- Python 3.9+
- Claude Code dengan plugin superpowers
- `curl` (macOS/Linux) atau PowerShell 5+ (Windows)

## Uninstall

```bash
./uninstall.sh
```

## Catatan

- Logo UPI (`assets/upi-logo.png`) tidak disertakan dalam repo. Tambahkan secara manual sebelum distribusi.
- Konfigurasi tersimpan di `~/.claude/magang-tools/config.json` — jalankan `/rpl-magang:init` ulang jika pedoman berubah.
- Repo: https://github.com/dikdns/upi-rpl-laporan-magang
