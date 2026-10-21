"""Check that Python and the local Ollama server are ready.

Usage, from the repository root:
    .venv\\Scripts\\python scripts\\check_env.py
"""

import sys

from compliance_copilot.config import load_settings
from compliance_copilot.health import MIN_PYTHON, check_ollama, check_python_version


def main() -> int:
    settings = load_settings()
    all_ok = True

    python = check_python_version()
    if python.ok:
        print(f"[OK] Python {python.version}")
    else:
        min_version = ".".join(str(part) for part in MIN_PYTHON)
        print(f"[ERREUR] Python {python.version} : la version {min_version} ou plus récente est requise.")
        all_ok = False

    ollama = check_ollama(settings.ollama_base_url)
    if ollama.ok:
        print(f"[OK] Ollama {ollama.version} répond sur {settings.ollama_base_url}")
        if ollama.models:
            print("     Modèles installés : " + ", ".join(ollama.models))
        else:
            print("     Aucun modèle installé pour l'instant.")
    else:
        print(f"[ERREUR] Ollama ne répond pas sur {settings.ollama_base_url} ({ollama.error}).")
        print("         Lancez l'application Ollama, puis relancez ce script.")
        all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
