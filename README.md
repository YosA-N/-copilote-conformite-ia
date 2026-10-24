# Copilote IA de conformité

Assistant open source qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, en **citant toujours l'article source**. Tout tourne **en local** et gratuitement, grâce à [Ollama](https://ollama.com).

**Statut :** projet en construction. Le copilote répond aux questions en citant ses sources, en ligne de commande. La qualité des réponses est en cours d'évaluation.

> Ce copilote aide à comprendre les textes. Il ne remplace pas un conseil juridique.

## Prérequis

- Python 3.11 ou plus récent
- [Ollama](https://ollama.com) installé et lancé, avec deux modèles :
  - `bge-m3` pour la recherche (`ollama pull bge-m3`, 1,2 Go) ;
  - `ministral-3:3b` pour rédiger les réponses (`ollama pull ministral-3:3b`, 3,0 Go).
- Une carte graphique NVIDIA avec 4 Go de mémoire suffit (testé sur une GTX 1650) ; sans elle, tout fonctionne sur le processeur, mais plus lentement.

## Installation (Windows, PowerShell)

```powershell
git clone https://github.com/YosA-N/copilote-conformite-ia.git
cd copilote-conformite-ia
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

Le fichier `.env` contient votre configuration locale (adresse d'Ollama, modèles utilisés). Il n'est jamais envoyé sur GitHub.

## Vérifier l'environnement

```powershell
.venv\Scripts\python scripts\check_env.py   # Python et Ollama répondent-ils ?
.venv\Scripts\python -m pytest              # lancer les tests
```

## Préparer le corpus

```powershell
.venv\Scripts\python scripts\download_sources.py   # télécharge les textes dans data\raw\ (une seule fois)
.venv\Scripts\python scripts\build_corpus.py       # découpe les textes dans data\processed\chunks.jsonl
```

Chaque article devient un morceau de texte (**chunk**). Un article trop long (plus de 4 000 caractères) est découpé par paragraphe, par définition ou par point, et chaque morceau rappelle le règlement, l'article et son titre. Chaque chunk garde aussi ses métadonnées : règlement, article ou annexe, titre, chapitre, paragraphe, lien EUR-Lex vers l'article et date de version.

Les textes viennent de [Cellar](https://op.europa.eu/fr/web/cellar), le dépôt de l'Office des publications qui alimente EUR-Lex : EUR-Lex refuse les téléchargements faits par des scripts. Si le téléchargement échoue, le script explique comment enregistrer le fichier à la main depuis EUR-Lex.

## Chercher dans les textes

```powershell
.venv\Scripts\python scripts\build_index.py                          # construit l'index (environ 7 min la première fois)
.venv\Scripts\python scripts\search.py "Dois-je désigner un DPO ?"   # affiche les 5 passages les plus proches
.venv\Scripts\python scripts\evaluate_retrieval.py                   # mesure la qualité sur eval\questions_v0.jsonl
```

Chaque chunk est transformé en vecteur (**embedding**) par le modèle `bge-m3`, via Ollama, puis rangé dans une base [Chroma](https://www.trychroma.com) locale (`data/index/`). Une question est transformée de la même façon : les passages dont le vecteur est le plus proche (similarité cosinus) sont affichés avec leur score et leur lien EUR-Lex. L'index n'est recalculé que si `chunks.jsonl` ou le modèle changent. Le modèle et le matériel utilisé (carte graphique ou processeur) se règlent dans `.env`.

`evaluate_retrieval.py` pose les 10 questions de `eval/questions_v0.jsonl` et indique, pour chacune, le rang du premier article attendu, puis le **hit@1** (l'article attendu arrive en premier) et le **hit@5** (il est dans les 5 premiers passages).

## Poser une question

```powershell
.venv\Scripts\python scripts\ask.py "Dois-je désigner un DPO ?"
.venv\Scripts\python scripts\ask.py "Dois-je désigner un DPO ?" --show-passages   # montre aussi les passages lus par le modèle
```

Le copilote cherche les 5 passages les plus proches, puis le modèle `ministral-3:3b` rédige une réponse à partir de ces seuls passages, numérotés [1] à [5], en les citant. Le texte s'affiche au fur et à mesure.

Le code ajoute ensuite :
- la liste des sources (règlement, article, titre, lien EUR-Lex, date de version), construite à partir des métadonnées et non par le modèle ;
- une alerte si la réponse cite un passage inexistant, ne cite aucun passage, ou a été coupée par la limite de longueur ;
- l'avertissement « Information, pas un conseil juridique ».

Comptez environ 30 secondes par question avec une carte graphique de 4 Go.

`scripts\answer_questions.py` pose les 10 questions de test et 2 questions hors sujet, puis enregistre les réponses brutes dans `eval/answers_v0.md` pour relecture.

## Mémoire de la carte graphique

Le modèle de génération se règle dans `.env` :

| Réglage | Valeur par défaut | Rôle |
|---|---|---|
| `LLM_NUM_CTX` | `8192` | Taille du contexte en tokens : passages + question + réponse |
| `LLM_NUM_GPU` | `99` | Couches du modèle placées sur la carte graphique (99 = toutes, le plus rapide) |
| `LLM_TEMPERATURE` | `0.1` | Basse : réponses plus stables et plus fidèles aux passages |
| `LLM_MAX_TOKENS` | `700` | Longueur maximale d'une réponse ; une réponse coupée est signalée |

Avec ces valeurs, `ministral-3:3b` occupe 3,87 Go sur une carte de 4 Go. Si le copilote affiche « Mémoire insuffisante », par exemple parce qu'une autre application utilise la carte graphique, essayez dans cet ordre :
1. baissez `LLM_NUM_CTX` à `6144` (3,66 Go mesurés) ou `4096` (3,45 Go) ;
2. baissez `LLM_NUM_GPU`, par exemple à `20` : une partie du modèle passe alors sur le processeur ;
3. laissez `LLM_NUM_GPU` vide : Ollama choisit lui-même, mais la réponse est environ 4 fois plus lente.

## Sources juridiques

| Texte | Version consolidée utilisée | Contenu repris |
|---|---|---|
| [RGPD — règlement (UE) 2016/679](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504) | 4 mai 2016 (rectificatif de 2018 intégré) | 99 articles |
| [AI Act — règlement (UE) 2024/1689](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727) | 27 juillet 2026 (intègre le règlement (UE) 2026/1744, « omnibus numérique sur l'IA ») | 119 articles et 14 annexes |

Les considérants ne sont pas repris. Les fiches pratiques de la [CNIL](https://www.cnil.fr) viendront plus tard.

**Mention de source.** Source : EUR-Lex, https://eur-lex.europa.eu — © Union européenne, 1998-2026. Les textes consolidés sont réutilisés sous licence [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr), conformément à la [décision 2011/833/UE](https://eur-lex.europa.eu/eli/dec/2011/833/oj). Modifications apportées : découpage en extraits (articles, paragraphes, définitions, points d'annexe) et suppression des marques de consolidation (▼B, ▼M1, ►C1…). Les textes consolidés sont un outil de documentation : seul fait foi le texte publié au *Journal officiel de l'Union européenne*.

## Licence

MIT — voir [LICENSE](LICENSE).
