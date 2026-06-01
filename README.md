<div align="center">

# rpl-magang

**magang, ~~tulis~~ prompting, beres**

Plugin Claude Code buat anak RPL UPI Cibiru. Bikin logbook, laporan magang, sama PKS yang udah ngikut pedoman dan format dokumen kampus.

Capek kan copy-paste mulu terus ngerapihin DOCX satu-satu? Udah, kasih PDF pedoman sekali doang, sisanya biar plugin yang handle. Dari struktur bab, cover, lembar pengesahan, heading, sampe PKS, gas otomatis semua.

![Status](https://img.shields.io/badge/status-public%20beta-orange) ![Versi](https://img.shields.io/badge/versi-1.0.0--beta.1-blue) ![Lisensi](https://img.shields.io/badge/lisensi-MIT-green)

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

> 🧪 Ini masih **public beta**. Udah jalan dan udah gw tes pake pedoman RPL UPI Cibiru Versi ke-6, tapi belum dites buat semua skenario. Jadi tetep cek hasil DOCX-nya dulu sebelum dikumpulin, jangan main kirim aja. Detail batasannya ada di [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md).

## Skills

Ada empat, masing-masing ngerjain satu hal doang.

| Skill | Buat apa |
|-------|----------|
| `/rpl-magang:init` | Jalanin ini dulu, sekali aja. Dia baca PDF pedoman lu, ambil struktur bab, format, sama komponen penilaian. Lu review, terus disimpen. |
| `/rpl-magang:logbook` | Bikin logbook mingguan atau dua mingguan (Catatan Harian & Kehadiran) jadi DOCX. Bisa satuan, batch, atau import dari file lama. |
| `/rpl-magang:laporan` | Nulis laporan per bab, terus `compile` jadi satu DOCX lengkap. |
| `/rpl-magang:pks` | Bikin PKS dari template resmi. Yang diisi cuma bagian mitranya doang. |
| `/rpl-magang:penilaian-penyelia` | generate Lembar Penilaian Penyelia (form penilaian dari pembimbing lapangan) sesuai pedoman, siap dicetak di KOP mitra |

Urutannya simpel. `init` sekali, terus `logbook` tiap minggu, lanjut `laporan` per bab, `compile`, baru `pks`.

## How It Works

Semua ngikut pedoman lu. Pas `init`, plugin baca PDF pedoman, terus ambil struktur bab, aturan format (font, margin, spasi, gaya kutipan), sama komponen penilaian. Lu cek dulu bener apa engga, baru disimpen. Skill yang lain tinggal pake data ini, jadi gausah ngetik ulang.

Skillnya yang nanya, script Python yang bikin DOCX-nya. Tiap skill bakal nanya hal yang dibutuhin, lu jawab pake bahasa bebas aja santai, nanti dia yang rapihin jadi dokumen sesuai format kampus.

Laporan yang keluar udah jadi, ga setengah-setengah:
- Cover sama Lembar Pengesahan satu halaman penuh sesuai pedoman, ukuran font 12/10/12/14, lengkap sama logo UPI
- Heading ngikut gaya kampus. BAB itu 14pt tebal di tengah, sub-bab 12pt tebal di kiri, warnanya hitam, bukan biru bawaan Word yang suka bikin laporan keliatan template banget itu
- Mau nempel foto kegiatan? Tulis aja `![keterangan](path)`, nanti gambarnya masuk otomatis plus caption "Gambar X.Y"
- KATA PENGANTAR, DAFTAR ISI, DAFTAR PUSTAKA, LAMPIRAN dibikin kayak judul bab
- Kertasnya A4, margin sama font ngikut config

Buat PKS, plugin niru cara manual lu. Jadi bukan ngarang dari nol, tapi ngisi bagian kosong di template resmi. Semua pasal sama bagian UPI tetep sama persis, yang ganti cuma data mitra sama tanggal. Mirip lu ganti bagian yang distabilo kuning, cuma ini otomatis.

## Why

Laporan magang kampus tuh ribet parah formatnya. Ukuran font beda-beda tiap baris, struktur bab baku, cover wajib satu halaman, PKS-nya legal jadi pasalnya gaboleh diutak-atik. Ngerjain manual? Gampang banget typo, format geser, atau malah lupa bagian wajib kayak Lembar Pengesahan, which is fatal banget pas dicek dosen.

Plugin ini ngurus bagian ribetnya, biar lu bisa fokus ke isi. Yang penting dinilai kan sisi RPL atau software engineering-nya, bukan rapihnya margin.

## Examples

```
1. /rpl-magang:init                  # sekali aja, arahin ke PDF pedoman
2. /rpl-magang:logbook               # logbook tiap minggu
3. /rpl-magang:laporan cover
4. /rpl-magang:laporan lembar-pengesahan
5. /rpl-magang:laporan bab1 ... bab4 # tulis tiap bab
6. /rpl-magang:laporan compile       # ekspor jadi DOCX lengkap
7. /rpl-magang:pks                   # bikin PKS
```

## Dependencies

- Python 3.9 ke atas. Library `python-docx`, `pdfplumber`, `Pillow` keinstall otomatis, gausah mikir
- Claude Code
- `curl` (macOS/Linux) atau PowerShell 5+ (Windows)

## Docs

| Dokumen | Isinya |
|---------|--------|
| [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) | Batasan beta, apa yang belum dites dan mesti hati-hati |
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
