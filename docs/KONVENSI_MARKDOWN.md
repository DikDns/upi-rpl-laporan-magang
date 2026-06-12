# Konvensi Markdown (buat Penulis Laporan)

Engine `generate_laporan.py` ngerti beberapa sintaks markdown khusus pas
nyusun file `.md` jadi DOCX. Skill (`/rpl-magang:laporan`, `laporan-bab-*`)
udah otomatis nulis sesuai aturan ini, tapi kalau lu edit draft `.md` sendiri,
ikutin tabel di bawah biar hasil DOCX-nya rapi.

## Sintaks yang didukung

| Sintaks | Efek di DOCX |
|---------|--------------|
| `**tebal**` | **bold** |
| `*miring*` atau `_miring_` | *italic* — pakai buat istilah teknis/asing |
| `` `kode` `` | monospace — buat perintah/nama berkas |
| `# JUDUL` | Heading 1 (judul bab/front-matter, ke tengah, masuk DAFTAR ISI) |
| `## Sub` / `### Sub-sub` | Heading 2/3 (kiri, masuk DAFTAR ISI) |
| `1. ...` / `2. ...` | numbered list — penomoran restart per list (ga numpuk antar bab) |
| `![keterangan](images/x.png)` (baris sendiri) | gambar + caption "Gambar B.N" + masuk DAFTAR GAMBAR |
| `Tabel: <judul>` (baris sendiri, di atas pipe table) | caption "Tabel B.N" + masuk DAFTAR TABEL |
| pipe table (`\| a \| b \|`) | tabel beneran |
| `[SIGN] ... [/SIGN]` | blok tanda tangan: tabel borderless rata kanan, baris kosong = ruang TTD basah |
| section `daftar-pustaka.md` | hanging indent APA otomatis |

### Contoh gambar

```markdown
![Dashboard aplikasi internal](images/dashboard.png)
```

→ gambar lebar 14cm, di tengah, caption "Gambar 3.1 Dashboard aplikasi internal".

### Contoh tabel + caption

```markdown
Tabel: Teknologi yang digunakan

| Kategori | Tools |
|----------|-------|
| Bahasa   | Go, Python |
| CI/CD    | GitLab CI |
```

→ caption "Tabel 3.1 Teknologi yang digunakan" + masuk DAFTAR TABEL.

### Contoh blok tanda tangan

```markdown
[SIGN]
Bandung, Juni 2026
Penulis,



Nama Mahasiswa
[/SIGN]
```

## Penomoran "Gambar/Tabel B.N"

Prefix `B` diambil dari nama file section (`bab3.md` → "Gambar 3.x", "Tabel 3.x").
Section dengan nama tak lazim jatuh ke penomoran berurutan biasa.

## Daftar Pustaka & sitasi (APA)

- Setiap klaim faktual/eksternal wajib sitasi in-text `(Penulis, Tahun)` di bab,
  plus entri yang cocok di `daftar-pustaka.md`.
- `daftar-pustaka.md` diawali `# DAFTAR PUSTAKA`, satu paragraf per sumber,
  urut alfabet, format APA-7, judul di-`_italic_`. Hanging indent otomatis.
- Sumber harus nyata & verifiable.

## Preferensi penulisan prosa (saran)

- Jangan double-label "Indonesia (_English_)" berulang-ulang.
- Pakai istilah natural (mis. "_tools_", bukan "perkakas") — istilah asing
  di-`_italic_`.
- Hindari titik dua pemberi contoh di prosa, pakai konjungsi.
- Konteks QA RPL pakai "verifikasi dan validasi kualitas perangkat lunak",
  bukan "penjaminan mutu".

## Catatan field Word

DAFTAR ISI, DAFTAR TABEL/GAMBAR, caption, dan nomor halaman pakai **field Word**
(TOC/SEQ). Pas dokumen dibuka pertama kali, field di-update otomatis
(`updateFields=true`). Di Google Docs murni, DAFTAR ISI tampil native tapi
table-of-figures/tables cuma snapshot — buka/Update sekali di LibreOffice/Word
atau ekspor PDF biar nomornya pasti benar.

## File yang TIDAK ikut di-compile

`generate_laporan.py` cuma nge-compile section yang dikenal (`cover`,
`lembar-pengesahan`, `kata-pengantar`, `daftar-pustaka`, `bab1..N`, lampiran
front/back-matter). Logbook, PKS, dan draft lain milik lu — ga ikut ke-compile
otomatis.
