# Copilote IA de conformité

Assistant open source qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, en **citant toujours l'article source**. Tout tourne **en local** et gratuitement, grâce à [Ollama](https://ollama.com).

**Statut :** projet en construction. Les textes de loi sont téléchargés et découpés ; le copilote ne répond pas encore aux questions.

> Ce copilote aide à comprendre les textes. Il ne remplace pas un conseil juridique.

## Prérequis

- Python 3.11 ou plus récent
- [Ollama](https://ollama.com) installé et lancé

## Installation (Windows, PowerShell)

```powershell
git clone https://github.com/YosA-N/-copilote-conformite-ia.git
cd .\-copilote-conformite-ia
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

## Sources juridiques

| Texte | Version consolidée utilisée | Contenu repris |
|---|---|---|
| [RGPD — règlement (UE) 2016/679](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504) | 4 mai 2016 (rectificatif de 2018 intégré) | 99 articles |
| [AI Act — règlement (UE) 2024/1689](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727) | 27 juillet 2026 (intègre le règlement (UE) 2026/1744, « omnibus numérique sur l'IA ») | 119 articles et 14 annexes |

Les considérants ne sont pas repris. Les fiches pratiques de la [CNIL](https://www.cnil.fr) viendront plus tard.

**Mention de source.** Source : EUR-Lex, https://eur-lex.europa.eu — © Union européenne, 1998-2026. Les textes consolidés sont réutilisés sous licence [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr), conformément à la [décision 2011/833/UE](https://eur-lex.europa.eu/eli/dec/2011/833/oj). Modifications apportées : découpage en extraits (articles, paragraphes, définitions, points d'annexe) et suppression des marques de consolidation (▼B, ▼M1, ►C1…). Les textes consolidés sont un outil de documentation : seul fait foi le texte publié au *Journal officiel de l'Union européenne*.

## Licence

MIT — voir [LICENSE](LICENSE).
