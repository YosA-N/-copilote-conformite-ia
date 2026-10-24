# CLAUDE.md — Copilote IA de conformité

## Le projet

Projet personnel open source (licence MIT, dépôt GitHub public) : un assistant **RAG** (Retrieval-Augmented Generation) qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, et qui **cite toujours l'article source**.

L'auteur débute en programmation : Claude écrit le code, l'auteur valide. Tout doit rester **gratuit** et tourner **en local**.

## Machine de l'auteur

- Windows 11, Python 3.13.2, Git 2.48, Ollama 0.40.7
- 16 Go de RAM, NVIDIA GTX 1650 avec **4 Go de VRAM** → le modèle de génération doit peser au plus ~3 Go (quantifié Q4), contexte limité à ~8K tokens.
- **VRAM** : `bge-m3` (1,2 Go) + `ministral-3:3b` (3,0 Go) dépassent ensemble les 4 Go. Mesuré (séance 3) : sur la carte graphique, `bge-m3` occupe 0,69 Go et traite environ 300 tokens/s ; sur le CPU (option Ollama `num_gpu=0`), il est presque aussi rapide, avec des vecteurs identiques à 0,9999 près. Les questions passent donc par le CPU (`QUERY_EMBEDDING_DEVICE=cpu`) pour laisser la carte graphique au modèle de génération.

## Choix techniques

- **Langage** : Python (paquet `src/compliance_copilot/`).
- **Corpus** : RGPD (règlement (UE) 2016/679), AI Act (règlement (UE) 2024/1689) et quelques fiches CNIL. Découpage (**chunking**) **par article**.
  - Versions consolidées figées dans `src/compliance_copilot/sources.py` : RGPD du 04/05/2016 (99 articles), AI Act du 27/07/2026 (intègre 2026/1744 : 119 articles, 14 annexes). Pas de considérants.
  - Téléchargement par **Cellar** (`publications.europa.eu/resource/celex/…`) : EUR-Lex renvoie un défi anti-robot aux scripts, ne pas chercher à le contourner.
  - Mention de source EUR-Lex obligatoire (CC BY 4.0) : voir le README.
  - Taille des chunks : 4 000 caractères au plus (~1 000 tokens, `MAX_CHUNK_CHARS` dans `corpus.py`). C'est un point de départ : des morceaux plus petits seront testés à l'étape d'évaluation.
- **Embeddings** : modèle open source multilingue, en local (servi par Ollama). Par défaut : `bge-m3`.
  - Interface `Embedder` dans `embeddings.py` (un autre backend n'a besoin que de `model` et `embed()`), envoi par lots de 16, `truncate=false` (erreur plutôt que texte coupé en silence).
- **Base vectorielle** : Chroma 1.5.9, persistante dans `data/index/`, distance cosinus.
  - Télémétrie désactivée et `embedding_function=None` : Chroma ne télécharge jamais son propre modèle.
  - `data/index/manifest.json` garde l'empreinte de `chunks.jsonl` et le nom du modèle : l'index n'est recalculé que s'ils changent. Sous Windows, on supprime la collection, jamais le dossier (fichiers verrouillés).
- **Évaluation** : `eval/questions_v0.jsonl` (10 questions types, articles attendus vérifiés dans le texte), mesurée par `evaluate_retrieval.py` (hit@1, hit@5, rang du premier article attendu). On mesure d'abord ; on ne retouche pas les questions pour améliorer le score.
  - Mesure de référence (séance 3, `bge-m3`, chunks de 4 000 caractères au plus) : **hit@1 = 6/10, hit@5 = 7/10**. Échecs : q03 durée de conservation (rang 6, réponse partielle dans le corpus), q04 mention d'information (rang 20), q10 IA générative au travail (art. 4 non trouvé dans les 20 premiers). Les sigles DPO et AIPD passent (rang 1). Pistes à étudier à la séance 5.
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
7. **Relecture** : ne jamais fusionner une Pull Request avant que l'auteur confirme l'avoir relue. Après l'ouverture d'une PR, s'arrêter et attendre cette confirmation.

## Structure

```
src/compliance_copilot/   code du paquet (config.py, health.py, …)
scripts/                  scripts lancés à la main (check_env.py, …)
tests/                    tests pytest (hors ligne : ils ne demandent pas Ollama)
data/raw/                 textes sources téléchargés (ignoré par Git)
data/processed/           articles découpés : chunks.jsonl (ignoré par Git)
data/index/               index Chroma et manifest.json (ignoré par Git)
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
.venv\Scripts\python scripts\build_index.py            # calculer les embeddings et remplir Chroma
.venv\Scripts\python scripts\search.py "question"      # afficher les 5 passages les plus proches
.venv\Scripts\python scripts\evaluate_retrieval.py     # mesurer hit@1 et hit@5
.venv\Scripts\python -m pytest                         # lancer les tests
```

Pas besoin d'« activer » le venv : on appelle directement `.venv\Scripts\python`.
