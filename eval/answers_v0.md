# Réponses du copilote — v0

Générées le 24/10/2026 à 22:40 par `scripts/answer_questions.py`, **sans aucune retouche**, pour relecture.

- Génération : `ministral-3:3b` via Ollama 0.40.10 — température 0.1, contexte 8192 tokens, couches sur la carte graphique : toutes, 700 tokens au plus par réponse
- Recherche : `bge-m3` (sur CPU), 5 passages par question
- Corpus : versions consolidées RGPD du 2016-05-04, AI Act du 2026-07-27
- Questions : `eval/questions_v0.jsonl` (10) et `eval/questions_offtopic_v0.jsonl` (2, hors sujet)

| # | Question | Citations | Alertes du code | Temps total |
|---|---|---|---|---|
| q01 | Dois-je désigner un DPO ? | [1] | — | 11 s |
| q02 | Dois-je tenir un registre des traitements ? | [1], [3], [5] | — | 19 s |
| q03 | Combien de temps puis-je garder les données de mes clients ou adhérents ? | [1] | — | 16 s |
| q04 | Que dois-je mettre dans la mention d'information d'un formulaire ? | [2], [3], [5] | — | 26 s |
| q05 | Une personne demande l'accès à ses données : quel délai pour répondre ? | [3] | — | 16 s |
| q06 | J'ai eu une fuite de données : que faire, et en combien de temps ? | [1], [2] | — | 22 s |
| q07 | Quand faut-il faire une analyse d'impact (AIPD) ? | [1], [4], [5] | — | 13 s |
| q08 | Mon chatbot doit-il dire aux clients qu'il est une IA ? | [1] | — | 15 s |
| q09 | Puis-je utiliser une IA pour trier des CV ? | [3], [4] | — | 28 s |
| q10 | Mes salariés ou bénévoles utilisent une IA générative : ai-je des obligations ? | [1], [2], [4], [5] | — | 21 s |
| h01 | Quel est le taux de TVA en France ? | aucune | La réponse ne cite aucun passage : elle n'est peut-être pas fondée sur les textes. Vérifiez-la avec les sources. | 15 s |
| h02 | Comment faire une déclaration d'impôts ? | [1], [2], [3], [4] | — | 17 s |

## q01 — Dois-je désigner un DPO ?

Article attendu : RGPD art. 37 — passage [1].

### Réponse du copilote

> Oui, vous devez désigner un **Délégué à la Protection des Données (DPO)** si votre activité principale consiste en un traitement à grande échelle de données personnelles, comme le précise le passage [1].
>
> Plus précisément, cela s'applique si vos activités de base incluent :
> - Un suivi régulier et systématique à grande échelle des personnes concernées (paragraphe **b** du [1]),
> - Un traitement à grande échelle de données sensibles (comme les données liées à la santé, les origines raciales, etc.) ou des condamnations pénales (paragraphe **c** du [1]).
>
> Si votre association ou PME ne remplit **aucun** de ces critères, vous n'avez pas besoin de désigner un DPO. Cependant, si vous êtes une **association ou un organisme représentant des responsables de traitement**, le RGPD impose aussi la désignation d'un DPO (paragraphe **4** du [1]).

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] RGPD — règlement (UE) 2016/679, article 37 : Désignation du délégué à la protection des données (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_37
Passages consultés mais non cités :
  [2] RGPD — règlement (UE) 2016/679, article 38 : Fonction du délégué à la protection des données
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_38
  [3] AI Act — règlement (UE) 2024/1689, article 3, définition 4 : Définitions
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_3
  [4] RGPD — règlement (UE) 2016/679, article 39 : Missions du délégué à la protection des données
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_39
  [5] RGPD — règlement (UE) 2016/679, article 27 : Représentants des responsables du traitement ou des sous-traitants qui ne sont pas établis dans l'Union
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_27

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 4.4 s · génération 6.8 s (2086 tokens lus, 204 écrits, 45.6 tokens/s)

## q02 — Dois-je tenir un registre des traitements ?

Article attendu : RGPD art. 30 — passage [1].

### Réponse du copilote

> Oui, **vous devez tenir un registre des activités de traitement** si vous êtes responsable du traitement de données à caractère personnel, **sauf si votre association ou votre PME compte moins de 250 employés** et que le traitement ne présente **aucun risque pour les droits et libertés des personnes concernées**, ne soit **occasionnel**, ou ne porte pas sur des données sensibles (comme des condamnations pénales ou des données de santé, sauf exceptions comme celles mentionnées en [3]).
>
> [1] et [5]

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] RGPD — règlement (UE) 2016/679, article 30 : Registre des activités de traitement (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_30
  [3] RGPD — règlement (UE) 2016/679, article 9, paragraphe 3 : Traitement portant sur des catégories particulières de données à caractère personnel (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_9
  [5] RGPD — règlement (UE) 2016/679, article 6, paragraphe 1 : Licéité du traitement (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_6
Passages consultés mais non cités :
  [2] AI Act — règlement (UE) 2024/1689, article 12 : Enregistrement
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_12
  [4] RGPD — règlement (UE) 2016/679, article 5 : Principes relatifs au traitement des données à caractère personnel
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_5

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 17.1 s (2327 tokens lus, 113 écrits, 45.7 tokens/s)

## q03 — Combien de temps puis-je garder les données de mes clients ou adhérents ?

Article attendu : RGPD art. 5 — absent des passages donnés au modèle.

### Réponse du copilote

> D'après le RGPD, **vous devez conserver les données de vos clients ou adhérents pendant une durée maximale de 10 ans après la fin de leur relation avec votre association ou entreprise**, sauf si des règles spécifiques locales ou sectorielles (comme celles des services financiers) imposent une durée plus longue [1].
>
> Si vous êtes une association ou une PME, **les passages ne précisent pas de durée minimale de conservation** pour les données personnelles. Vous pouvez donc les supprimer dès que les besoins légaux ou opérationnels le justifient (ex. : fin du traitement des données).

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] AI Act — règlement (UE) 2024/1689, article 18 : Conservation des documents (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_18
Passages consultés mais non cités :
  [2] RGPD — règlement (UE) 2016/679, article 12, paragraphe 3 : Transparence des informations et des communications et modalités de l'exercice des droits de la personne concernée
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_12
  [3] AI Act — règlement (UE) 2024/1689, article 36, paragraphe 9 : Modifications apportées aux notifications
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_36
  [4] RGPD — règlement (UE) 2016/679, article 88 : Traitement de données dans le cadre des relations de travail
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_88
  [5] AI Act — règlement (UE) 2024/1689, article 44 : Certificats
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_44

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 14.3 s (1839 tokens lus, 126 écrits, 47.1 tokens/s)

## q04 — Que dois-je mettre dans la mention d'information d'un formulaire ?

Article attendu : RGPD art. 13 — absent des passages donnés au modèle.

### Réponse du copilote

> Pour la **mention d'information** dans un formulaire lié à un système d’IA (comme un chatbot ou un outil d’assistance), vous devez inclure :
> - **Une description générale du système d’IA** (selon [2], point a) et [5], point 1.a) : nom, version, destination et interaction avec le matériel/logiciels externes.
> - **Les modalités d’utilisation** (comme les règles d’acceptabilité, selon [5], point 1.b) et [3], point 1.b).
>
> *Exemple concret* :
> *"Ce système d’IA interagit avec votre matériel via une API. Il est conçu pour [préciser la tâche principale]. Les règles d’utilisation sont : [exemples : pas de données personnelles sensibles, pas de contenu illégal]. Version X, distribuée via [canal : téléchargement, API]."*
>
> ---
> **À éviter** :
> - Ne mentionnez pas les données d’entraînement (sauf si elles sont **explicites** et **volontaires**, ce qui n’est pas précisé dans les passages).
> - Ne décrivez pas les **ressources techniques** (comme la consommation d’énergie ou les paramètres du modèle) dans la mention d’information classique, sauf si elles sont **obligatoires** pour la transparence (ex. : taille de la fenêtre de contexte, selon [3], point 2.b)).

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [2] AI Act — règlement (UE) 2024/1689, annexe IV, point 1 : Documentation technique visée à l'article 11, paragraphe 1 (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_IV
  [3] AI Act — règlement (UE) 2024/1689, annexe XII : Informations relatives à la transparence visées à l'article 53, paragraphe 1, point b) – documentation technique pour les fournisseurs de modèles d'IA à usage général aux fournisseurs en aval qui intègrent le modèle dans leur système d'IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_XII
  [5] AI Act — règlement (UE) 2024/1689, annexe XI : Documentation technique visée à l'article 53, paragraphe 1, point a) – documentation technique pour les fournisseurs de modèles d'IA à usage général (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_XI
Passages consultés mais non cités :
  [1] AI Act — règlement (UE) 2024/1689, article 91 : Pouvoir de demander de la documentation et des informations
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_91
  [4] AI Act — règlement (UE) 2024/1689, annexe V : Déclaration UE de conformité
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_V

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 24.2 s (2689 tokens lus, 303 écrits, 44.2 tokens/s)

## q05 — Une personne demande l'accès à ses données : quel délai pour répondre ?

Article attendu : RGPD art. 12 — passage [1].

### Réponse du copilote

> Vous devez répondre dans un délai **raisonnable**, mais sans dépasser **un mois** après avoir obtenu ses données, **sauf si les données sont utilisées pour communiquer avec elle** (alors délai au moment de la première communication) ou si elles sont partagées avec un autre destinataire (alors délai au moment de la première communication) [3].
>
> Si vous utilisez des données pour communiquer avec la personne concernée, la réponse doit être donnée **au moment de la première communication** [3].

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [3] RGPD — règlement (UE) 2016/679, article 14, paragraphe 3 : Informations à fournir lorsque les données à caractère personnel n'ont pas été collectées auprès de la personne concernée (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_14
Passages consultés mais non cités :
  [1] RGPD — règlement (UE) 2016/679, article 12, paragraphe 3 : Transparence des informations et des communications et modalités de l'exercice des droits de la personne concernée
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_12
  [2] RGPD — règlement (UE) 2016/679, article 12, paragraphe 4 : Transparence des informations et des communications et modalités de l'exercice des droits de la personne concernée
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_12
  [4] RGPD — règlement (UE) 2016/679, article 33 : Notification à l'autorité de contrôle d'une violation de données à caractère personnel
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_33
  [5] RGPD — règlement (UE) 2016/679, article 15 : Droit d'accès de la personne concernée
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_15

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 13.6 s (1773 tokens lus, 112 écrits, 47.1 tokens/s)

## q06 — J'ai eu une fuite de données : que faire, et en combien de temps ?

Article attendu : RGPD art. 33 ou RGPD art. 34 — passage [1].

### Réponse du copilote

> Pour une fuite de données à caractère personnel, vous devez :
> - **Notifier l’autorité de contrôle** dans les **meilleurs délais, idéalement sous 72 heures** (sinon, vous devez justifier le retard) [1].
> - **Informer les personnes concernées** si la fuite présente un **risque élevé** pour leurs droits et libertés (dans les meilleurs délais) [2].
>
> *Explications* :
> - Le délai de **72 heures** s’applique pour la notification à l’autorité de contrôle (ex : CNIL en France) [1].
> - La notification aux personnes concernées n’est obligatoire que si le risque est élevé (ex : données sensibles volées ou exposées) [2]. Sinon, vous pouvez éviter cette étape si des mesures de sécurité (chiffrement, etc.) atténuent le danger [2].
>
> *(Pas de délai précis pour l’AI Act dans ce cas, car il s’agit d’une fuite de données personnelles, pas d’un système d’IA.)*

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] RGPD — règlement (UE) 2016/679, article 33 : Notification à l'autorité de contrôle d'une violation de données à caractère personnel (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_33
  [2] RGPD — règlement (UE) 2016/679, article 34 : Communication à la personne concernée d'une violation de données à caractère personnel (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_34
Passages consultés mais non cités :
  [3] RGPD — règlement (UE) 2016/679, article 17 : Droit à l'effacement («droit à l'oubli»)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_17
  [4] AI Act — règlement (UE) 2024/1689, article 18 : Conservation des documents
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_18
  [5] AI Act — règlement (UE) 2024/1689, article 73, paragraphe 2 : Signalement d’incidents graves
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_73

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 20.0 s (2393 tokens lus, 222 écrits, 44.9 tokens/s)

## q07 — Quand faut-il faire une analyse d'impact (AIPD) ?

Article attendu : RGPD art. 35 — passage [1].

### Réponse du copilote

> Vous devez faire une **analyse d'impact relative à la protection des données (AIPD)** si :
> - Vous traitez des données personnelles **automatisées** (comme un profilage) et prenez des décisions importantes pour une personne (ex. : refus d’un prêt, exclusion d’un système), **ou** si ces décisions affectent significativement cette personne de manière similaire [1].
> - Vous traitez **à grande échelle** des données sensibles (comme celles sur la santé, la vie privée, ou des condamnations pénales) [1].
> - Vous surveillez **systématiquement et à grande échelle** une zone publique (comme une caméra vidéo en continu dans un espace accessible au public) [1].
>
> *(Les passages [4] et [5] précisent que l’AIPD est aussi obligatoire si le traitement utilise des technologies nouvelles ou présente un **risque élevé** pour les droits des personnes, même sans les cas cités ci-dessus.)*

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] RGPD — règlement (UE) 2016/679, article 35, paragraphe 3 : Analyse d'impact relative à la protection des données (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_35
  [4] RGPD — règlement (UE) 2016/679, article 35, paragraphe 1 : Analyse d'impact relative à la protection des données (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_35
  [5] RGPD — règlement (UE) 2016/679, article 35, paragraphe 4 : Analyse d'impact relative à la protection des données (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_35
Passages consultés mais non cités :
  [2] RGPD — règlement (UE) 2016/679, article 35, paragraphe 11 : Analyse d'impact relative à la protection des données
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_35
  [3] RGPD — règlement (UE) 2016/679, article 35, paragraphe 7 : Analyse d'impact relative à la protection des données
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_35

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 10.7 s (1006 tokens lus, 206 écrits, 49.2 tokens/s)

## q08 — Mon chatbot doit-il dire aux clients qu'il est une IA ?

Article attendu : AI Act art. 50 — passage [1].

### Réponse du copilote

> Oui, votre chatbot doit généralement **informer les clients qu’il s’agit d’un système d’IA**, sauf si cela est **évident** pour une personne raisonnablement attentive dans le contexte d’utilisation [1].
>
> Cette obligation ne s’applique pas si votre chatbot est utilisé **uniquement pour la prévention ou la détection d’infractions pénales** (avec des garanties spécifiques pour les droits des tiers) [1].

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 1 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
Passages consultés mais non cités :
  [2] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 2 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
  [3] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 4 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
  [4] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 3 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
  [5] AI Act — règlement (UE) 2024/1689, article 25, paragraphe 4 : Responsabilités tout au long de la chaîne de valeur de l’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_25

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 12.7 s (1698 tokens lus, 96 écrits, 48.0 tokens/s)

## q09 — Puis-je utiliser une IA pour trier des CV ?

Article attendu : AI Act annexe III, point 4 ou AI Act art. 26 — passage [3].

### Réponse du copilote

> Non, vous ne pouvez pas utiliser une IA pour trier des CV dans le cadre d’un système d’IA à haut risque comme celui visé à l’article 35 du RGPD et de l’article 39 du règlement (UE) 2018/1725, **sauf si** cette IA est développée dans le cadre d’un **bac à sable réglementaire** et que toutes les conditions du passage [4] sont remplies, notamment :
> - Les données doivent être **nécessaires** pour éviter un biais grave (ex. : discrimination) et ne peuvent pas être traitées avec des données anonymisées ou synthétiques.
> - Les données doivent être **isolées** dans un environnement sécurisé et protégées (pas de partage avec d’autres systèmes).
> - Les biais doivent être **détectés et corrigés** strictement, avec des garanties techniques (comme la pseudonymisation).
> - Les données doivent être **supprimées** dès que le biais est corrigé ou la période de conservation écoulée.
>
> Si votre IA est **destinée uniquement au recrutement** (comme dans le passage [3]), elle relève d’un système à haut risque et doit respecter ces règles strictes.
>
> ---
> **Autre cas possible** :
> Si vous utilisez une IA **pour un projet d’intérêt public** (ex. : améliorer l’égalité des chances dans le recrutement), vous pourriez être dans le cadre du **bac à sable réglementaire** (passage [4]), mais **seulement si** :
> - Les données sont **collectées légalement** pour un autre usage (ex. : bases de données publiques).
> - Les conditions techniques et de sécurité sont strictement respectées (passage [4], points **b, d, g**).
> - Les résultats sont **documentés** et les risques surveillés (passage [4], points **c, i**).
>
> Sinon, le tri de CV relève d’un **risque élevé de discrimination** et doit être encadré par des règles strictes (RGPD + AI Act).

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [3] AI Act — règlement (UE) 2024/1689, annexe III, point 4 : Systèmes d'IA à haut risque visés à l'article 6, paragraphe 2 (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_III
  [4] AI Act — règlement (UE) 2024/1689, article 59, paragraphe 1, points a) à i) : Traitement ultérieur de données à caractère personnel en vue du développement de certains systèmes d’IA dans l’intérêt public dans le cadre du bac à sable réglementaire de l’IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_59
Passages consultés mais non cités :
  [1] AI Act — règlement (UE) 2024/1689, article 59, paragraphe 1, point j) : Traitement ultérieur de données à caractère personnel en vue du développement de certains systèmes d’IA dans l’intérêt public dans le cadre du bac à sable réglementaire de l’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_59
  [2] AI Act — règlement (UE) 2024/1689, article 4 bis : Traitement de catégories particulières de données à caractère personnel à des fins de détection et de correction des biais
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_4a
  [5] AI Act — règlement (UE) 2024/1689, article 59, paragraphe 3 : Traitement ultérieur de données à caractère personnel en vue du développement de certains systèmes d’IA dans l’intérêt public dans le cadre du bac à sable réglementaire de l’IA
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_59

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 25.8 s (2516 tokens lus, 438 écrits, 44.1 tokens/s)

## q10 — Mes salariés ou bénévoles utilisent une IA générative : ai-je des obligations ?

Article attendu : AI Act art. 4 — absent des passages donnés au modèle.

### Réponse du copilote

> Oui, vous avez des obligations selon le type d’IA utilisée et son usage, mais elles dépendent de la situation précise :
>
> - **Si vos salariés ou bénévoles génèrent ou manipulent des images, vidéos ou textes** (ex. : deepfakes, contenus créatifs, informations publiques), **il faut indiquer explicitement que ces contenus ont été générés ou modifiés par une IA**, sauf si :
>   - L’usage est **autorisé par la loi** pour la **prévention/détection des infractions pénales** ou des **enquêtes** [1].
>   - Le contenu fait partie d’une **œuvre artistique, satirique ou fictive** : il suffit de mentionner *l’existence* de ces contenus générés par IA sans en détailler la nature [1].
>   - Le texte est **publié pour informer le public sur des questions d’intérêt public** : il faut indiquer que le texte a été généré par IA **sauf si** :
>     - L’usage est **autorisé par la loi** pour la **prévention/détection des infractions** [1],
>     - Le contenu a fait l’objet d’un **contrôle humain** et une **responsabilité éditoriale** est assumée [1].
>
> - **Si vos salariés ou bénévoles interagissent directement avec une IA** (ex. : chatbots, assistants virtuels), **il faut les informer qu’ils interagissent avec un système d’IA**, sauf si :
>   - Cela ressort **clairement du contexte** (ex. : un chatbot dont l’identité est évidente) [2].
>   - L’usage est **autorisé par la loi** pour la **prévention/détection des infractions** [2].
>
> ---
> **Pour les systèmes à haut risque** (ex. : recrutement automatisé, diagnostics médicaux), vérifiez aussi :
> - Les obligations contractuelles avec les fournisseurs (ex. : accès aux données techniques pour le contrôle humain) [4].
> - L’enregistrement du système dans la base de données de l’UE si applicable [5].
>
> *Si votre usage ne rentre dans aucun des cas exemptés, précisez explicitement la source IA dans vos contenus ou interactions.*

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 4 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
  [2] AI Act — règlement (UE) 2024/1689, article 50, paragraphe 1 : Obligations de transparence pour les fournisseurs et les déployeurs de certains systèmes d’IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_50
  [4] AI Act — règlement (UE) 2024/1689, article 25, paragraphe 4 : Responsabilités tout au long de la chaîne de valeur de l’IA (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_25
  [5] AI Act — règlement (UE) 2024/1689, article 26, paragraphe 8 : Obligations incombant aux déployeurs de systèmes d’IA à haut risque (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_26
Passages consultés mais non cités :
  [3] AI Act — règlement (UE) 2024/1689, article 26, paragraphe 3 : Obligations incombant aux déployeurs de systèmes d’IA à haut risque
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_26

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 19.3 s (1459 tokens lus, 479 écrits, 47.1 tokens/s)

## h01 — Quel est le taux de TVA en France ?

Question hors sujet : aucun article attendu, la réponse devrait dire que les passages ne suffisent pas.

### Réponse du copilote

> Les passages fournis ne mentionnent **aucun détail sur la TVA** (taux, exceptions, etc.). Ils ne concernent que les amendes administratives du RGPD et de l'AI Act.
>
> Je ne peux donc pas répondre à votre question sur le taux de TVA en France.

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  aucune
Passages consultés mais non cités :
  [1] RGPD — règlement (UE) 2016/679, article 83, paragraphe 5 : Conditions générales pour imposer des amendes administratives
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_83
  [2] AI Act — règlement (UE) 2024/1689, article 99, paragraphe 5 : Sanctions
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_99
  [3] RGPD — règlement (UE) 2016/679, article 83, paragraphe 4 : Conditions générales pour imposer des amendes administratives
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_83
  [4] AI Act — règlement (UE) 2024/1689, article 99, paragraphe 4 : Sanctions
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_99
  [5] AI Act — règlement (UE) 2024/1689, article 101 : Amendes applicables aux fournisseurs de modèles d’IA à usage général
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_101
Attention : La réponse ne cite aucun passage : elle n'est peut-être pas fondée sur les textes. Vérifiez-la avec les sources.

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 13.0 s (1859 tokens lus, 61 écrits, 47.1 tokens/s)

## h02 — Comment faire une déclaration d'impôts ?

Question hors sujet : aucun article attendu, la réponse devrait dire que les passages ne suffisent pas.

### Réponse du copilote

> D'après les passages fournis, **la déclaration d'impôts n'est pas mentionnée ni définie dans le RGPD ni dans l'AI Act**. Ces textes ne concernent que :
> - **Le RGPD** : les droits des personnes (comme réclamer une violation de données) et la transparence des traitements de données [1], [4].
> - **L'AI Act** : la déclaration de conformité pour les systèmes d’IA à haut risque [2], [3].
>
> Aucun des passages ne traite des obligations fiscales classiques (comme les déclarations d’impôts). Il s’agit donc d’une question hors du cadre de ces textes.

### Sources, contrôles et avertissement (ajoutés par le code)

```text
Sources citées :
  [1] RGPD — règlement (UE) 2016/679, article 77 : Droit d'introduire une réclamation auprès d'une autorité de contrôle (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_77
  [2] AI Act — règlement (UE) 2024/1689, article 47 : Déclaration UE de conformité (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_47
  [3] AI Act — règlement (UE) 2024/1689, annexe V : Déclaration UE de conformité (version du 2026-07-27)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#anx_V
  [4] RGPD — règlement (UE) 2016/679, article 12, paragraphe 5 : Transparence des informations et des communications et modalités de l'exercice des droits de la personne concernée (version du 2016-05-04)
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02016R0679-20160504#art_12
Passages consultés mais non cités :
  [5] AI Act — règlement (UE) 2024/1689, article 91 : Pouvoir de demander de la documentation et des informations
      https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:02024R1689-20260727#art_91

Information, pas un conseil juridique : vérifiez les textes officiels cités et, en cas de doute, demandez l'avis d'un professionnel ou de la CNIL.
```

Temps : recherche 2.1 s · génération 15.3 s (1941 tokens lus, 139 écrits, 46.1 tokens/s)
