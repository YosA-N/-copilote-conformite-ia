# Copilote IA de conformité

Assistant open source qui répond **en français** aux questions des PME et des associations sur le **RGPD** et l'**AI Act**, en **citant toujours l'article source**. Tout tourne **en local** et gratuitement, grâce à [Ollama](https://ollama.com).

**Statut :** projet en construction. Pour l'instant, seule la mise en place est faite : le copilote ne répond pas encore aux questions.

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

## Sources juridiques

- [Règlement (UE) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj) — RGPD
- [Règlement (UE) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj) — AI Act
- Fiches pratiques de la [CNIL](https://www.cnil.fr)

## Licence

MIT — voir [LICENSE](LICENSE).
