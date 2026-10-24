# CLAUDE.md — Copilote IA de conformité

## Le projet

Projet personnel open source (licence MIT, dépôt GitHub public) : un assistant **RAG** (Retrieval-Augmented Generation) qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, et qui **cite toujours l'article source**.

L'auteur débute en programmation : Claude écrit le code, l'auteur valide. Tout doit rester **gratuit** et tourner **en local**.

## Machine de l'auteur

- Windows 11, Python 3.13.2, Git 2.48, Ollama 0.40.7
- 16 Go de RAM, NVIDIA GTX 1650 avec **4 Go de VRAM** → le modèle de génération doit peser au plus ~3 Go (quantifié Q4), contexte limité à ~8K tokens.
- **VRAM** : `bge-m3` (1,2 Go) + `ministral-3:3b` (3,0 Go) dépassent ensemble les 4 Go. À l'étape RAG, tester les embeddings sur le CPU (option Ollama `num_gpu=0`) pour laisser la carte graphique au modèle de génération.

## Choix techniques

- **Langage** : Python (paquet `src/compliance_copilot/`).
- **Corpus** : RGPD (règlement (UE) 2016/679), AI Act (règlement (UE) 2024/1689) et quelques fiches CNIL. Découpage (**chunking**) **par article**.
  - Versions consolidées figées dans `src/compliance_copilot/sources.py` : RGPD du 04/05/2016 (99 articles), AI Act du 27/07/2026 (intègre 2026/1744 : 119 articles, 14 annexes). Pas de considérants.
  - Téléchargement par **Cellar** (`publications.europa.eu/resource/celex/…`) : EUR-Lex renvoie un défi anti-robot aux scripts, ne pas chercher à le contourner.
  - Mention de source EUR-Lex obligatoire (CC BY 4.0) : voir le README.
- **Embeddings** : modèle open source multilingue, en local (servi par Ollama). Par défaut : `bge-m3`.
- **Base vectorielle** : locale (Chroma).
- **Génération** : petit modèle via Ollama, derrière une **interface interchangeable** : changer de modèle = modifier une ligne dans `.env`. Par défaut : `ministral-3:3b`.
- **Interface web** : Streamlit, plus tard.
- **Dépendances** : on n'ajoute une bibliothèque qu'à l'étape qui en a besoin, avec une version épinglée (`==`) dans `requirements.txt`.

## Règles

1. **Langues** : code, noms (fichiers, fonctions, variables) et messages de commit en **anglais**. README, interface et réponses du copilote en **français**.
2. **Sources** : chaque réponse du copilote cite sa source (règlement + numéro d'article, ou fiche CNIL). Pas de source trouvée = le dire, ne pas inventer.
3. **Secrets** : jamais de secret dans le dépôt. Le fichier `.env` est ignoré par Git ; seul `.env.example` (valeurs d'exemple) est commité.
4. **Accord préalable** : ne rien télécharger (modèles Ollama, gros fichiers) et ne rien pousser (`git push`) sur GitHub sans l'accord de l'auteur.
5. **Explications** : après chaque étape, expliquer en 3 à 5 phrases simples ce qui a été fait et pourquoi, en donnant les termes techniques anglais (par exemple « environnement virtuel (**virtual environment**) »).
6. **Méthode** : présenter un plan et attendre la validation avant les changements importants. Travailler sur une branche, pas directement sur `main`.

## Structure

```
src/compliance_copilot/   code du paquet (config.py, health.py, …)
scripts/                  scripts lancés à la main (check_env.py, …)
tests/                    tests pytest (hors ligne : ils ne demandent pas Ollama)
data/raw/                 textes sources téléchargés (ignoré par Git)
data/processed/           articles découpés, index (ignoré par Git)
eval/                     questions-tests d'évaluation (versionné, contrairement à data/)
```

## Commandes utiles (PowerShell, depuis la racine du dépôt)

```powershell
python -m venv .venv                                   # créer l'environnement virtuel
.venv\Scripts\python -m pip install -r requirements.txt  # installer les dépendances
copy .env.example .env                                 # créer sa configuration locale
.venv\Scripts\python scripts\check_env.py              # vérifier Python et Ollama
.venv\Scripts\python scripts\download_sources.py       # télécharger les textes (une seule fois)
.venv\Scripts\python scripts\build_corpus.py           # découper les textes en chunks
.venv\Scripts\python -m pytest                         # lancer les tests
```

Pas besoin d'« activer » le venv : on appelle directement `.venv\Scripts\python`.
