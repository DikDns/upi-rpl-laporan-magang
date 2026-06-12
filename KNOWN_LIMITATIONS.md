# Batasan yang Diketahui (Release Candidate)

> Status: **`1.0.0-rc.1`** — fungsional, tapi belum diuji menyeluruh.
> Selalu **periksa hasil DOCX secara manual** sebelum dikumpulkan.

Skill ini sudah diuji pada **pedoman RPL UPI Cibiru "Versi ke-6 MBKM/P3NK"**
dan satu set data contoh. Hal-hal berikut **belum diuji / berpotensi
bermasalah**:

## Parsing pedoman (`init`)
- Hanya divalidasi pada pedoman Versi ke-6. **Versi pedoman lain** atau
  format PDF berbeda bisa salah parse — selalu cek di Step 4 review.
- PDF hasil scan / berbasis gambar (tanpa teks) **tidak bisa diparse**
  (jatuh ke fallback manual).
- Komponen penilaian & struktur bab diekstrak heuristik; review wajib.

## Laporan (`laporan`)
- Distribusi vertikal cover & lembar pengesahan memakai jarak tetap yang
  ditune untuk A4 — pada konten/nama yang sangat panjang bisa bergeser.
- Gambar dipaksa selebar 14cm; **foto kecil bisa pecah**, foto portрait
  tinggi bisa makan banyak ruang vertikal.
- Penomoran "Gambar X.Y" berbasis nama file section (bab3 → 3.x); section
  dengan nama tak lazim memakai penomoran berurutan biasa.
- Skenario peran magang **non-coding** (admin, desain, QA) hanya didukung
  lewat reminder RPL — kualitas akhir tetap tergantung input mahasiswa.

## PKS (`pks`)
- Pengisian terikat pada **token di template bawaan** (diturunkan dari
  "Cth. PKS atau MoU.docx"). Jika template resmi direvisi dengan tata
  letak berbeda, token perlu dipetakan ulang.
- Tanggal terbilang **diketik manual** — tidak ada validasi/konversi
  otomatis dari tanggal numerik.

## Field Word & output (compile)
- DAFTAR ISI, DAFTAR TABEL/GAMBAR, caption, dan nomor halaman pakai **field
  Word** (TOC/SEQ). Engine sudah set `updateFields=true`, jadi field
  ter-update saat file dibuka pertama kali di **Word/LibreOffice**. Kalau
  belum keisi, buka & "Update Field" (atau ekspor PDF) sekali.
- Di **Google Docs murni**, DAFTAR ISI tampil native, tapi
  table-of-figures/tables hanya snapshot — buka/Update sekali di
  LibreOffice/Word, atau ekspor PDF, biar nomornya pasti benar.
- Output tambahan **ODT/PDF** (`--also`) butuh **LibreOffice** terpasang;
  kalau tidak ada, hanya `.docx` yang dibuat. Default `--also` = `odt` saja.

## Lingkungan
- Diuji di **macOS**. Path Linux seharusnya sama; **Windows (PowerShell)**
  belum diuji end-to-end.
- Butuh **Python 3.9+** dengan `python-docx`, `pdfplumber`, `Pillow`.
- Untuk ekspor ODT/PDF: **LibreOffice** (opsional).

## Cara melapor
Temukan bug? Buka issue di
<https://github.com/DikDns/upi-rpl-laporan-magang/issues> — sertakan versi
pedoman, langkah, dan (kalau bisa) DOCX hasilnya.
