#!/usr/bin/env python3
"""
Extract hyperlink annotations (URIs) embedded in a PDF — e.g. a logbook
exported from ClickUp/Notion/Docs where each entry links to a Merge Request,
task, or doc. Dependency-free: scans raw + zlib-inflated streams for
`/URI (...)`, so it works without pdfplumber/pypdf installed.

The logbook skill uses this to enrich daily activities: the extracted
ClickUp / GitLab URLs are then fetched via the ClickUp MCP and `glab` to
pull real titles, IDs, and statuses into the activity descriptions.

Usage:
  python extract_pdf_links.py --pdf "Logbook.pdf"
  python extract_pdf_links.py --pdf "Logbook.pdf" --only clickup,gitlab

Output (stdout): JSON {success, count, links:[{uri, kind}]}
  kind ∈ {clickup, gitlab, google, email, other}
"""

import argparse
import json
import re
import sys
import zlib
from pathlib import Path


def classify(uri: str) -> str:
    u = uri.lower()
    if "clickup.com" in u:
        return "clickup"
    if "gitlab" in u:
        return "gitlab"
    if "docs.google.com" in u or "drive.google.com" in u:
        return "google"
    if u.startswith("mailto:"):
        return "email"
    return "other"


def extract(pdf_path: Path) -> list:
    data = pdf_path.read_bytes()
    uris = set()
    pat = re.compile(rb"/URI\s*\(([^)]*)\)")
    # URIs sitting in the raw bytes
    for m in pat.finditer(data):
        uris.add(m.group(1).decode("latin1", "replace"))
    # URIs inside FlateDecode streams
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            inflated = zlib.decompress(m.group(1))
        except Exception:
            continue
        for mm in pat.finditer(inflated):
            uris.add(mm.group(1).decode("latin1", "replace"))
    return sorted(uris)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--only", default="",
                    help="comma-separated kinds to keep (e.g. clickup,gitlab)")
    args = ap.parse_args()

    pdf = Path(args.pdf).expanduser()
    if not pdf.exists():
        print(json.dumps({"success": False, "error": f"Not found: {pdf}"}))
        sys.exit(1)

    keep = {k.strip() for k in args.only.split(",") if k.strip()}
    links = [{"uri": u, "kind": classify(u)} for u in extract(pdf)]
    if keep:
        links = [l for l in links if l["kind"] in keep]
    print(json.dumps({"success": True, "count": len(links), "links": links},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
