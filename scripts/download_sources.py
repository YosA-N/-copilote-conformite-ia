"""Download the consolidated legal texts once, into data/raw/.

EUR-Lex answers scripts with an anti-bot challenge, so the texts come from Cellar,
the Publications Office repository behind EUR-Lex, which is meant for programs.
A file that is already in data/raw/ is never downloaded again (unless --force).

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\download_sources.py [--force]
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import date, datetime

from compliance_copilot.config import RAW_DIR
from compliance_copilot.corpus import read_amendments
from compliance_copilot.sources import SOURCES, USER_AGENT, Source

MANIFEST_PATH = RAW_DIR / "sources.json"


def fetch(source: Source) -> bytes:
    request = urllib.request.Request(
        source.cellar_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/xhtml+xml", "Accept-Language": "fra"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        if response.status != 200:
            raise OSError(f"HTTP {response.status} (page anti-robot ?)")
        return response.read()


def check_content(source: Source, html: str) -> None:
    """Make sure the file is the expected consolidated text, not an error or challenge page."""
    base_celex = source.celex.split("-")[0]
    if "TEXTE consolidé" not in html or base_celex not in html:
        raise ValueError(f"ce fichier n'est pas le texte consolidé {source.celex}")


def print_manual_steps(source: Source, error: Exception) -> None:
    path = RAW_DIR / source.raw_filename
    print(f"[ERREUR] {source.name} : téléchargement impossible ({error}).")
    print("         Marche à suivre manuelle :")
    print(f"         1. Ouvrez cette page dans votre navigateur : {source.eurlex_html_url}")
    print("         2. Enregistrez-la (Ctrl+S), type « Page web, HTML uniquement », sous ce nom exact :")
    print(f"            {path}")
    print("         3. Relancez ce script : il utilisera le fichier enregistré.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Télécharge les textes consolidés dans data/raw/.")
    parser.add_argument("--force", action="store_true", help="retélécharger même si le fichier existe")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else {}
    all_ok = True

    for source in SOURCES:
        path = RAW_DIR / source.raw_filename
        previous = manifest.get(source.key, {})
        try:
            if path.exists() and not args.force:
                content = path.read_bytes()
                method = previous.get("method", "manuel")
                downloaded_at = previous.get("downloaded_at") or datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
                status = "déjà présent"
            else:
                content = fetch(source)
                method, downloaded_at, status = "cellar", date.today().isoformat(), "téléchargé"
            html = content.decode("utf-8")
            check_content(source, html)
        except (OSError, ValueError) as error:
            print_manual_steps(source, error)
            all_ok = False
            continue

        if status == "téléchargé":
            path.write_bytes(content)
        manifest[source.key] = {
            "name": source.name,
            "reference": source.reference,
            "celex": source.celex,
            "version_date": source.version_date,
            "downloaded_at": downloaded_at,
            "method": method,
            "url": source.cellar_url if method == "cellar" else source.eurlex_html_url,
            "eurlex_url": source.eurlex_url,
            "file": source.raw_filename,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
            "amendments": read_amendments(html),
        }
        print(f"[OK] {source.name} ({source.celex}, version du {source.version_date}) : {status}, {len(content):,} octets")
        for amendment in manifest[source.key]["amendments"]:
            print(f"     {amendment}")

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
