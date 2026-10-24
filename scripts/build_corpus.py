"""Cut the downloaded legal texts into chunks and write data/processed/chunks.jsonl.

Run scripts/download_sources.py first.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\build_corpus.py
"""

import json
import sys

from compliance_copilot.config import PROCESSED_DIR, RAW_DIR
from compliance_copilot.corpus import build_chunks, missing_lines
from compliance_copilot.sources import SOURCES

OUTPUT_PATH = PROCESSED_DIR / "chunks.jsonl"


def main() -> int:
    manifest_path = RAW_DIR / "sources.json"
    if not manifest_path.exists():
        print("[ERREUR] data/raw/sources.json est absent : lancez d'abord scripts\\download_sources.py.")
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    all_chunks = []
    all_ok = True
    for source in SOURCES:
        entry = manifest.get(source.key)
        if entry is None or entry["celex"] != source.celex:
            print(f"[ERREUR] {source.name} : version {source.celex} absente de data/raw/sources.json.")
            all_ok = False
            continue
        html = (RAW_DIR / entry["file"]).read_text(encoding="utf-8")
        units, chunks = build_chunks(source, html)
        all_chunks.extend(chunks)

        articles = sum(unit.unit_type == "article" for unit in units)
        annexes = sum(unit.unit_type == "annex" for unit in units)
        sizes = [chunk.char_count for chunk in chunks]
        split_units = len({(chunk.unit_type, chunk.number) for chunk in chunks if chunk.part_count > 1})
        lost = [
            (unit.anchor, line)
            for unit in units
            for line in missing_lines(unit, [chunk for chunk in chunks if chunk.source_url.endswith(f"#{unit.anchor}")])
        ]
        print(f"{source.name} — {source.reference} (version du {source.version_date}, téléchargée le {entry['downloaded_at']})")
        for amendment in entry.get("amendments", []):
            print(f"  intègre {amendment}")
        print(f"  articles : {articles} (attendu : {source.expected_articles})")
        print(f"  annexes  : {annexes} (attendu : {source.expected_annexes})")
        print(f"  chunks   : {len(chunks)}, dont {split_units} articles ou annexes découpés en plusieurs morceaux")
        print(f"  taille   : {sum(sizes) / len(sizes):,.0f} caractères en moyenne, {max(sizes):,} au maximum")
        print(f"  texte perdu au découpage : {len(lost)} ligne(s)")
        for anchor, line in lost[:5]:
            print(f"    {anchor} : {line[:100]}")
        if lost:
            all_ok = False
        if (articles, annexes) != (source.expected_articles, source.expected_annexes):
            print("  [ERREUR] Les nombres ne correspondent pas : la structure du texte a peut-être changé.")
            all_ok = False
        elif source.count_note:
            print(f"  note     : {source.count_note}")
        print()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as output:
        for chunk in all_chunks:
            output.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
    print(f"{len(all_chunks)} chunks écrits dans {OUTPUT_PATH.relative_to(PROCESSED_DIR.parents[1])}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
