# Berkontribusi

Makasih udah mau bantu! Proyek ini **release candidate** — laporan bug &
masukan sangat dihargai.

## Lapor bug / minta fitur
Buka [issue](https://github.com/DikDns/upi-rpl-laporan-magang/issues).
Untuk bug, sertakan:
- Versi pedoman yang dipakai
- Skill + langkah yang dijalankan
- Yang diharapkan vs yang terjadi
- Kalau bisa: file DOCX hasil + PDF pedoman (sensor data pribadi)

## Setup development
```bash
git clone https://github.com/DikDns/upi-rpl-laporan-magang
cd upi-rpl-laporan-magang
./install.sh          # deteksi repo lokal, install dari sini
```
Restart Claude Code → skill aktif sebagai `/rpl-magang:*`.

### Struktur repo
```
.claude-plugin/   metadata plugin + marketplace
skills/*/SKILL.md alur tiap skill (Claude-driven)
scripts/*.py      mesin generate DOCX (python-docx)
templates/        template PKS resmi (tokenized)
install.sh/.ps1   installer + registrasi (cache, marketplace, settings)
```

### Alur kerja
- **Skill** (`SKILL.md`) = orkestrasi percakapan; **script** = generate DOCX.
- Edit script di `scripts/`, lalu sync ke `~/.claude/magang-tools/scripts/`
  untuk uji cepat (atau jalankan `./install.sh` ulang).
- Uji generator langsung: `~/.claude/magang-tools/venv/bin/python
  scripts/generate_*.py --help`.
- Selalu verifikasi DOCX hasil sebelum commit (lihat `KNOWN_LIMITATIONS.md`).

## Commit
Conventional Commits (`feat:`, `fix:`, `docs:`, …), subjek ringkas,
jelaskan *why* di body kalau tidak obvious.

## Lisensi
Kontribusi tunduk pada lisensi [MIT](LICENSE).
