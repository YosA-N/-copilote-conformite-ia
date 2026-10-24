# CLAUDE.md — Copilote IA de conformité

## Le projet

Projet personnel open source (licence MIT, dépôt GitHub public) : un assistant **RAG** (Retrieval-Augmented Generation) qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, et qui **cite toujours l'article source**.

L'auteur débute en programmation : Claude écrit le code, l'auteur valide. Tout doit rester **gratuit** et tourner **en local**.

## Machine de l'auteur

- Windows 11, Python 3.13.2, Git 2.48, Ollama 0.40.10 (mis à jour automatiquement par Ollama pendant la séance 4 ; avant : 0.40.7)
- 16 Go de RAM, NVIDIA GTX 1650 avec **4 Go de VRAM** → le modèle de génération doit peser au plus ~3 Go (quantifié Q4), contexte limité à ~8K tokens.
- **VRAM** : `bge-m3` (1,2 Go) + `ministral-3:3b` (3,0 Go) dépassent ensemble les 4 Go. Mesuré (séance 3) : sur la carte graphique, `bge-m3` occupe 0,69 Go et traite environ 300 tokens/s ; sur le CPU (option Ollama `num_gpu=0`), il est presque aussi rapide, avec des vecteurs identiques à 0,9999 près. Les questions passent donc par le CPU (`QUERY_EMBEDDING_DEVICE=cpu`) pour laisser la carte graphique au modèle de génération.
- **Mesures de `ministral-3:3b`** (séance 4, Q4_K_M, 3,8 milliards de paramètres, 26 couches, module de vision inclus) :
  - Laissé à Ollama, il n'est placé qu'à 45-55 % sur la carte graphique et génère à 10-15 tokens/s, soit environ 50 s par réponse.
  - Avec toutes les couches forcées (`num_gpu=99`), il tient entièrement en VRAM et génère à **44 tokens/s** : 3,45 Go avec `num_ctx=4096`, 3,66 Go avec 6144, **3,87 Go avec 8192** (sur 4 Go).
  - Choix : `LLM_NUM_CTX=8192` et `LLM_NUM_GPU=99`. Le pire prompt (5 chunks de 4 000 caractères) approche 6 000 tokens, et un prompt type en fait environ 2 000.
  - En cas d'erreur de mémoire : baisser `LLM_NUM_CTX`, puis `LLM_NUM_GPU`.
  - La lecture du prompt reste vers 160 tokens/s. Une question coûte environ 30 s : recherche sur CPU 2 à 4 s, lecture du prompt environ 12 s, rédaction environ 7 s, plus environ 5 s de chargement à la première question.
  - `bge-m3` (CPU, 0 Go de VRAM) et `ministral` (GPU) restent chargés ensemble après la première question.

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
  - Interface `ChatModel` dans `llm.py` (`/api/chat` en streaming). Réglages dans `.env` : `LLM_NUM_CTX`, `LLM_NUM_GPU`, `LLM_TEMPERATURE=0.1`, `LLM_MAX_TOKENS=700`.
  - Messages d'erreur clairs prévus : Ollama arrêté, modèle absent, mémoire insuffisante.
  - `rag.py` : prompt système en français et passages numérotés [1]…[5]. Si le prompt risque de dépasser le contexte, les derniers passages sont retirés et un avertissement est affiché.
  - Ce que fait le **code**, et non le modèle :
    - citations normalisées (« [1b] » devient « [1] », y compris pendant le streaming) et vérifiées (passage inexistant, aucune citation) ;
    - sources construites à partir des métadonnées ;
    - réponse coupée signalée (`done_reason = "length"`) ;
    - avertissement « Information, pas un conseil juridique ».
  - Réponses de référence non retouchées : `eval/answers_v0.md`, produites par `answer_questions.py` (10 questions et 2 hors sujet).
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
.venv\Scripts\python scripts\ask.py "question"         # poser une question (réponse + sources)
.venv\Scripts\python scripts\answer_questions.py       # écrire eval/answers_v0.md (12 questions)
.venv\Scripts\python -m pytest                         # lancer les tests
```

Pas besoin d'« activer » le venv : on appelle directement `.venv\Scripts\python`.
