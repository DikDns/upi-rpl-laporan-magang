<div align="center">

# rpl-magang

**magang, ~~tulis~~ prompting, beres**

Plugin Claude Code buat anak RPL UPI Cibiru. Bikin logbook, laporan magang, sama PKS yang udah ngikut pedoman dan format dokumen kampus.

Capek kan copy-paste mulu terus ngerapihin DOCX satu-satu? Udah, kasih PDF pedoman sekali doang, sisanya biar plugin yang handle. Dari struktur bab, cover, lembar pengesahan, heading, sampe PKS, gas otomatis semua.

![Status](https://img.shields.io/badge/status-release%20candidate-orange) ![Versi](https://img.shields.io/badge/versi-1.0.0--rc.1-blue) ![Lisensi](https://img.shields.io/badge/lisensi-MIT-green)

</div>

## Installation

macOS / Linux:
```bash
curl -fsSL https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.sh | bash
```

Windows (PowerShell):
```powershell
irm https://raw.githubusercontent.com/DikDns/upi-rpl-laporan-magang/main/install.ps1 | iex
```

Abis install, restart Claude Code dulu ya biar skillnya nongol.

> 🧪 Ini **release candidate** (rc.1). Udah jalan dan udah gw tes pake pedoman RPL UPI Cibiru Versi ke-6 di skenario nyata (peran Test Engineer), tapi belum dites buat semua skenario. Jadi tetep cek hasil DOCX-nya dulu sebelum dikumpulin, jangan main kirim aja. Detail batasannya ada di [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

## Skills

| Skill | Buat apa |
|-------|----------|
| `/rpl-magang:init` | Jalanin ini dulu, sekali aja. Dia baca PDF pedoman lu, ambil struktur bab, format, sama komponen penilaian. Lu review, terus disimpen. **Bonus: dia juga otomatis bikin skill per bab** (lihat di bawah). |
| `/rpl-magang:logbook` | Bikin logbook mingguan atau dua mingguan (Catatan Harian & Kehadiran) jadi DOCX. Bisa satuan, batch, atau import dari file lama. |
| `/rpl-magang:laporan` | Nulis **front matter** laporan: `cover`, `lembar-pengesahan`, `kata-pengantar`. Panggil dengan section-nya, mis. `/rpl-magang:laporan cover`. |
| `/rpl-magang:laporan-bab-1` … `-bab-4` | **Digenerate otomatis pas `init`** — satu skill per bab, ngikut struktur & sub-section pedoman lu (jadi jumlahnya bisa beda kalau pedoman lu beda). Nuntun nulis tiap bab + ngingетin sisi RPL/SE sama sitasi APA. |
| `/rpl-magang:laporan-compile` | Gabungin semua section `.md` (front matter + bab) jadi satu DOCX lengkap — DAFTAR ISI otomatis, nomor halaman Roman/Arabic, bisa sekalian ekspor ODT/PDF. |
| `/rpl-magang:pks` | Bikin PKS dari template resmi. Yang diisi cuma bagian mitranya doang. |
| `/rpl-magang:penilaian-penyelia` | Bikin Lembar Penilaian Penyelia sesuai pedoman. Kosong buat diisi tangan, atau bisa prefill nilai dulu. Siap cetak. |

> ⚠️ Skill `laporan-bab-*` baru nongol **setelah lu jalanin `init`** (dia digenerate dari pedoman lu), terus **restart Claude Code**. Sebelum init, skill itu belum ada.

Urutannya simpel: `init` sekali → `logbook` tiap minggu → `laporan` (front matter) → `laporan-bab-1..N` per bab → `laporan-compile` → `pks` / `penilaian-penyelia`.

## How It Works

Semua ngikut pedoman lu. Pas `init`, plugin baca PDF pedoman, terus ambil struktur bab, aturan format (font, margin, spasi, gaya kutipan), sama komponen penilaian. Lu cek dulu bener apa engga, baru disimpen. Skill yang lain tinggal pake data ini, jadi gausah ngetik ulang.

`init` juga **bikin skill per bab otomatis** (`laporan-bab-1`, `-bab-2`, …) langsung dari struktur pedoman lu. Jadi sub-section tiap bab (mis. Latar Belakang, Tujuan, dst) udah ke-set sesuai pedoman, bukan template generik. Makanya abis `init` lu mesti **restart Claude Code** dulu biar skill-skill bab itu nongol.

Skillnya yang nanya, script Python yang bikin DOCX-nya. Tiap skill bakal nanya hal yang dibutuhin, lu jawab pake bahasa bebas aja santai, nanti dia yang rapihin jadi dokumen sesuai format kampus.

Laporan yang keluar udah jadi, ga setengah-setengah:
- Cover sama Lembar Pengesahan satu halaman penuh sesuai pedoman, ukuran font 12/10/12/14, lengkap sama logo UPI
- Heading ngikut gaya kampus. BAB itu 14pt tebal di tengah, sub-bab 12pt tebal di kiri, warnanya hitam, bukan biru bawaan Word yang suka bikin laporan keliatan template banget itu
- DAFTAR ISI, DAFTAR TABEL, sama DAFTAR GAMBAR digenerate otomatis (Word field) — kebaca pas dibuka di Word/LibreOffice
- Mau nempel foto kegiatan? Tulis aja `![keterangan](path)`, nanti gambarnya masuk otomatis plus caption "Gambar X.Y". Tabel juga bisa dikasih caption "Tabel X.Y"
- Sitasi & Daftar Pustaka format **APA** — klaim faktual ditandain biar lu kasih `(Penulis, Tahun)`, entri daftar pustaka otomatis hanging indent
- KATA PENGANTAR, DAFTAR ISI, DAFTAR PUSTAKA, LAMPIRAN dibikin kayak judul bab
- Kertasnya A4 portrait di semua halaman, margin sama font ngikut config
- Output utama DOCX; bisa sekalian **ODT/PDF** kalau ada LibreOffice

Sintaks markdown lengkap yang dikenali engine (italic, caption, blok tanda tangan, daftar pustaka) ada di [docs/KONVENSI_MARKDOWN.md](docs/KONVENSI_MARKDOWN.md).

Buat PKS, plugin niru cara manual lu. Jadi bukan ngarang dari nol, tapi ngisi bagian kosong di template resmi. Semua pasal sama bagian UPI tetep sama persis, yang ganti cuma data mitra sama tanggal. Mirip lu ganti bagian yang distabilo kuning, cuma ini otomatis.

## Why

Laporan magang kampus tuh ribet parah formatnya. Ukuran font beda-beda tiap baris, struktur bab baku, cover wajib satu halaman, PKS-nya legal jadi pasalnya gaboleh diutak-atik. Ngerjain manual? Gampang banget typo, format geser, atau malah lupa bagian wajib kayak Lembar Pengesahan, which is fatal banget pas dicek dosen.

Plugin ini ngurus bagian ribetnya, biar lu bisa fokus ke isi. Yang penting dinilai kan sisi RPL atau software engineering-nya, bukan rapihnya margin.

## Examples

### Alur kerja laporan

```
1. /rpl-magang:init                  # sekali aja, arahin ke PDF pedoman
   # (restart Claude Code biar skill laporan-bab-* nongol)
2. /rpl-magang:logbook               # logbook tiap minggu (paralel sama nulis laporan)
3. /rpl-magang:laporan cover         # front matter
   /rpl-magang:laporan lembar-pengesahan
   /rpl-magang:laporan kata-pengantar
4. /rpl-magang:laporan-bab-1         # tulis bab satu-satu (skill digenerate pas init)
   /rpl-magang:laporan-bab-2
   /rpl-magang:laporan-bab-3
   /rpl-magang:laporan-bab-4
5. /rpl-magang:laporan-compile       # gabung jadi satu DOCX lengkap (+ ODT/PDF opsional)
6. /rpl-magang:pks                   # bikin PKS
```

### Skills lainnya

```
/rpl-magang:logbook                  # buat logbook mingguan kapan aja
/rpl-magang:pks                      # buat PKS, bisa dipanggil mandiri
/rpl-magang:penilaian-penyelia       # generate lembar penilaian dari penyelia (siap cetak)
```

## Dependencies

- Python 3.9 ke atas. Library `python-docx`, `pdfplumber`, `Pillow` keinstall otomatis, gausah mikir
- Claude Code
- `curl` (macOS/Linux) atau PowerShell 5+ (Windows)
- **LibreOffice** — opsional, cuma kalau lu mau output ODT/PDF (`laporan-compile`). Tanpa ini tetep dapet DOCX

## Docs

| Dokumen | Isinya |
|---------|--------|
| [docs/KONVENSI_MARKDOWN.md](docs/KONVENSI_MARKDOWN.md) | Sintaks markdown yang dikenali engine (italic, caption gambar/tabel, blok tanda tangan, daftar pustaka) |
| [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) | Batasan rilis, apa yang belum dites dan mesti hati-hati |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cara lapor bug sama setup buat ngoprek |
| [CHANGELOG.md](CHANGELOG.md) | Apa aja yang berubah tiap rilis |

## Uninstall

```bash
./uninstall.sh
```

## License

[MIT](LICENSE).

<div align="center">

Dibikin buat anak RPL UPI Cibiru.
Nemu bug atau ada masukan? Mampir ke [Issues](https://github.com/DikDns/upi-rpl-laporan-magang/issues).

</div>
