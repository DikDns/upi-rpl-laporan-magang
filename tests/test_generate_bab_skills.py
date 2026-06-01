# tests/test_generate_bab_skills.py
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from generate_bab_skills import render_bab_skill, generate_all, BAB_MAP

SAMPLE_CONFIG = {
    "program": "Rekayasa Perangkat Lunak",
    "document_structure": {
        "bagian_isi": {
            "babI": {
                "title": "Pendahuluan",
                "sections": [
                    {"number": "1.1", "title": "Latar Belakang"},
                    {"number": "1.2", "title": "Manfaat & Tujuan"},
                ]
            },
            "babIII": {
                "title": "Pelaksanaan Kegiatan",
                "sections": [
                    {"number": "3.1", "title": "Rencana Kegiatan"},
                    {"number": "3.2", "title": "Implementasi"},
                ]
            },
        },
        "sections_flexible": True,
    }
}

def test_bab_map_covers_roman_numerals():
    assert BAB_MAP["babI"] == ("bab1", "BAB I")
    assert BAB_MAP["babII"] == ("bab2", "BAB II")
    assert BAB_MAP["babIII"] == ("bab3", "BAB III")
    assert BAB_MAP["babIV"] == ("bab4", "BAB IV")

def test_render_bab_skill_contains_verbatim_sections():
    bab_data = SAMPLE_CONFIG["document_structure"]["bagian_isi"]["babI"]
    result = render_bab_skill("babI", bab_data, sections_flexible=False)
    assert "name: laporan-bab-1" in result
    assert "1.1" in result
    assert "Latar Belakang" in result
    assert "1.2" in result
    assert "Manfaat & Tujuan" in result

def test_render_bab_skill_includes_bab_title():
    bab_data = SAMPLE_CONFIG["document_structure"]["bagian_isi"]["babI"]
    result = render_bab_skill("babI", bab_data, sections_flexible=False)
    assert "PENDAHULUAN" in result

def test_render_bab3_includes_flexibility_note():
    bab_data = SAMPLE_CONFIG["document_structure"]["bagian_isi"]["babIII"]
    result = render_bab_skill("babIII", bab_data, sections_flexible=True)
    assert "sections_flexible" in result or "role kamu" in result

def test_render_bab3_includes_image_rule():
    bab_data = SAMPLE_CONFIG["document_structure"]["bagian_isi"]["babIII"]
    result = render_bab_skill("babIII", bab_data, sections_flexible=True)
    assert "image-rule" in result or "foto dokumentasi" in result

def test_generate_all_writes_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = generate_all(SAMPLE_CONFIG, Path(tmpdir))
        assert len(paths) == 2  # babI and babIII
        names = [p.parent.name for p in paths]
        assert "laporan-bab-1" in names
        assert "laporan-bab-3" in names
        for p in paths:
            assert p.exists()
            assert p.name == "SKILL.md"
            content = p.read_text()
            assert "allowed-tools:" in content

def test_generate_all_description_has_section_titles():
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = generate_all(SAMPLE_CONFIG, Path(tmpdir))
        bab1_skill = next(p for p in paths if "bab-1" in str(p))
        content = bab1_skill.read_text()
        # description field should mention section titles for tab completion
        desc_line = next(l for l in content.splitlines() if l.startswith("description:"))
        assert "Latar Belakang" in desc_line or "Manfaat" in desc_line
