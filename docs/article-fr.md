# Planka + Hermes Kanban : un gestionnaire de travail hybride humain/IA

La plupart des todo apps ont été pensées pour des humains.

On crée une tâche. On l’assigne. On la déplace de colonne en colonne. On commente parfois. Puis le vrai travail se passe ailleurs : dans un IDE, un terminal, GitHub, Slack, Discord, Notion, ou simplement dans la tête de quelqu’un.

Avec les agents IA, ce modèle devient vite insuffisant.

Un agent ne doit pas seulement recevoir une instruction ponctuelle dans un chat. Il a besoin de contexte, d’un état durable, de critères d’acceptation, de permissions, d’un endroit où signaler ses blocages, et d’un mécanisme de handoff avec les humains.

C’est là que Planka devient intéressant.

Pas seulement comme “Trello open-source”. Comme couche de coordination entre humains et agents.

Dans notre expérimentation Planka + Hermes Kanban, Planka sert d’interface humaine et de source de vérité. Hermes Kanban agit comme orchestrateur derrière le board. Les cartes deviennent des unités de travail que les humains et les agents peuvent lire, modifier, commenter, bloquer, vérifier et reprendre.

L’objectif n’est pas de remplacer le chef de projet par une IA. L’objectif est plus pragmatique : transformer un board kanban en espace de travail partagé entre humains et agents.

## Le problème des agents hors-sol

La plupart des workflows IA commencent dans un chat :

> Peux-tu corriger ce bug ?
> Peux-tu auditer cette page ?
> Peux-tu me faire une synthèse ?

Ça marche pour des tâches courtes. Mais dès que le projet devient réel, les problèmes arrivent :

- l’agent oublie le contexte ;
- les décisions sont dispersées dans des conversations ;
- les humains ne savent pas ce qui a été tenté ;
- les tâches longues n’ont pas d’état visible ;
- les erreurs sont difficiles à auditer ;
- plusieurs agents peuvent se marcher dessus ;
- les handoffs humain ↔ IA sont flous ;
- l’agent peut continuer à travailler après un changement de priorité.

Un chat est une bonne interface d’entrée. Ce n’est pas un bon système de coordination.

La vraie question devient :

> Où vit le travail quand personne n’est en train de discuter avec l’agent ?

Pour nous, la réponse est : dans Planka.

## Planka comme source de vérité

Dans ce modèle, Planka n’est pas seulement un tableau de tâches. C’est la couche d’état canonique du système.

Chaque carte représente une unité de travail. Elle contient :

- l’objectif ;
- le contexte ;
- les liens utiles ;
- les fichiers ou services concernés ;
- les contraintes ;
- les critères d’acceptation ;
- les commentaires d’exécution ;
- les décisions humaines ;
- les blocages ;
- les résultats de vérification.

La carte devient un contrat.

Un humain peut ouvrir Planka et comprendre où en est le travail. Un agent peut lire la même carte et savoir quoi faire ensuite. Cette symétrie est importante : on évite de créer deux mondes séparés, un pour les humains et un pour les IA.

Le board devient une mémoire opérationnelle partagée.

## Hermes Kanban derrière Planka

Derrière Planka, Hermes Kanban joue le rôle d’orchestrateur.

Son travail n’est pas seulement de “faire la tâche”. Son travail est de gérer le cycle de vie de la tâche.

Hermes peut :

- lire les cartes Planka ;
- détecter les tâches prêtes à être prises ;
- enrichir le contexte ;
- découper une grosse tâche en sous-tâches ;
- choisir le bon modèle ou le bon worker ;
- lancer une exécution avec GPT-5.5, Grok 4.5, Composer 2.5 ou un worker spécialisé ;
- suivre la progression ;
- écrire des commentaires de heartbeat ;
- bloquer proprement si une décision humaine est nécessaire ;
- vérifier les résultats ;
- déplacer la carte dans la bonne colonne ;
- produire un résumé final.

Le board reste visible et manipulable par les humains. Hermes agit en arrière-plan comme couche d’automatisation et d’orchestration.

C’est ce qui distingue cette approche d’un simple “agent dans Slack”.

## Les colonnes comme protocole opérationnel

Dans un kanban classique, les colonnes sont souvent approximatives : Backlog, Doing, Done.

Dans un système hybride humain/IA, les colonnes deviennent un protocole.

Une structure simple :

```text
Backlog
To Do — Human
To Do — Agent
Worker / In Progress
Human Review
Blocked
Done
```

Chaque colonne a une signification opérationnelle.

`Backlog` contient les idées ou tâches pas encore prêtes.

`To Do — Human` contient les tâches qui demandent explicitement une action humaine.

`To Do — Agent` contient les tâches que Hermes peut prendre ou déléguer.

`Worker / In Progress` signifie qu’un humain ou un agent travaille activement sur la carte.

`Human Review` signifie que l’agent a préparé quelque chose, mais qu’une validation humaine est nécessaire.

`Blocked` signifie que le travail ne peut pas avancer sans information, credential, arbitrage ou décision.

`Done` signifie que la tâche est terminée et vérifiée.

Ce découpage évite un problème fréquent : les agents qui prennent trop d’initiative sur des actions sensibles. On peut laisser Hermes préparer une migration, un déploiement, une PR ou une publication, tout en exigeant une validation humaine avant l’action finale.

## La carte comme interface agentique

Une carte bien formée peut être lue par un agent comme un prompt structuré.

Exemple :

```markdown
Titre :
Auditer la page mobile /dashboard

Objectif :
Identifier les problèmes de lisibilité, performance et UX mobile.

Contexte :
Repo : ~/example-app
Page : /dashboard
Priorité : mobile first
Ne pas toucher au backend sauf nécessité.

Critères d’acceptation :
- Audit visuel mobile réalisé
- Liste priorisée des problèmes
- Fixs appliqués pour les problèmes P0/P1
- Test local ou capture avant/après
- Résumé posté en commentaire

Contraintes :
- Ne pas casser la home
- Pas de refonte globale
- Pas de déploiement sans validation humaine
```

Pour un humain, c’est une bonne carte projet.

Pour un agent, c’est un prompt exploitable.

Le format n’a pas besoin d’être rigide au début. Mais il doit contenir assez d’information pour éviter les ambiguïtés dangereuses.

## Les commentaires comme journal d’exécution

Les commentaires Planka sont essentiels.

Ils ne servent pas seulement à discuter. Ils créent une trace d’exécution.

Un agent peut poster :

```text
Hermes update:
- Repo inspecté : ~/example-app
- Fichier principal : app/dashboard/page.tsx
- Problème confirmé : overflow horizontal sur mobile 390px
- Fix en cours : réduction padding + wrapping cards
- Prochaine étape : lancer build + capture mobile
```

Ou, en cas de blocage :

```text
Blocked:
- Tentative : lancement du script de sync
- Erreur : token manquant dans l’environnement
- Besoin : confirmer où récupérer le credential ou fournir un environnement valide
- État : aucun fichier modifié
```

Ce niveau de trace change beaucoup de choses.

Un humain peut reprendre sans relire 200 messages de chat. Un autre agent peut continuer. On peut auditer ce qui s’est passé. Et surtout, on évite les “l’IA a dit que c’était fait” sans preuve.

## Les modèles comme workers spécialisés

Dans cette architecture, Hermes Kanban peut router le travail vers différents modèles ou environnements selon le besoin.

Par exemple :

- GPT-5.5 pour l’orchestration, le raisonnement long, la synthèse et la vérification ;
- Grok 4.5 pour certains workflows produit, recherche, analyse ou itération rapide ;
- Composer 2.5 pour les tâches de code, édition et intégration ;
- des lanes Codex/Cursor pour des modifications isolées dans un repo.

Le point important : le modèle n’est pas le produit.

Le produit, c’est le système de coordination.

Un worker peut changer. Le board reste. La carte reste. Les critères d’acceptation restent. Les logs restent. Le statut reste.

Cette séparation permet de tester plusieurs modèles sans reconstruire tout le workflow.

## Hermes orchestre, les workers exécutent

Une des règles les plus importantes : Hermes garde la responsabilité du cycle de vie.

Un worker peut produire un diff, un audit, une synthèse ou un rapport. Mais il ne doit pas forcément décider seul que la carte est terminée.

Le pattern sain :

1. Hermes lit la carte.
2. Hermes génère un prompt de travail contextualisé.
3. Un worker exécute dans un scope défini.
4. Le worker retourne un résultat.
5. Hermes relit, vérifie, teste ou demande une review humaine.
6. Hermes met à jour la carte.

Cette séparation évite un piège courant : confondre exécution et validation.

## Exemple de workflow complet

Prenons une tâche de développement :

> Corriger les problèmes de performance sur la page AI Signal.

① Un humain crée une carte dans Planka.

Il ajoute le contexte, la priorité et les contraintes.

② Hermes lit la carte.

Il détecte qu’elle est dans `To Do — Agent`.

③ Hermes enrichit ou découpe.

Si la tâche est trop large, il peut créer des sous-cartes : audit performance, analyse bundle, correction lazy loading, vérification mobile, changelog.

④ Hermes assigne un worker.

Selon la tâche, il lance GPT-5.5, Grok 4.5, Composer 2.5 ou une lane de code spécialisée.

⑤ Le worker exécute.

Il inspecte le repo, modifie les fichiers, lance les tests ou produit un diagnostic.

⑥ Hermes vérifie.

Il ne se contente pas de croire le worker. Il relit les diffs, lance les commandes nécessaires, vérifie que la sortie correspond à la carte.

⑦ La carte passe en `Human Review` ou `Done`.

Si une décision est nécessaire, la carte attend l’humain. Si tout est vérifié, elle passe en Done avec un commentaire final.

⑧ Le résumé reste dans Planka.

L’état du projet ne dépend pas d’un chat éphémère.

## Le vrai sujet : les permissions

Un gestionnaire de travail hybride doit gérer les permissions, pas seulement les tâches.

Toutes les actions ne se valent pas.

Un agent peut être autorisé à :

- lire un repo ;
- faire un audit ;
- proposer un plan ;
- créer une branche ;
- modifier un fichier ;
- lancer des tests.

Mais il peut avoir besoin d’une validation humaine pour :

- supprimer des données ;
- lancer un déploiement ;
- poster publiquement ;
- engager des coûts ;
- envoyer un email ;
- merger une PR ;
- modifier une configuration sensible.

Dans Planka, ça peut se traduire par des colonnes ou labels :

```text
Needs Approval
Safe to Execute
Destructive
Public Output
Credential Needed
Human Review
```

La carte devient donc aussi un objet de gouvernance.

## Pourquoi Planka plutôt qu’un outil AI-native ?

Il y a un avantage à partir d’un kanban simple et open-source : il est lisible par tout le monde.

Planka est suffisamment simple pour être utilisé comme interface humaine, mais suffisamment structuré pour devenir une base d’orchestration : projets, boards, listes, cartes, commentaires, labels, assignations, dates, historique.

On n’a pas forcément besoin d’un outil “AI-native” lourd au départ. On a besoin d’un bon modèle de coordination.

La simplicité est même un avantage : les humains comprennent immédiatement le système. Les agents peuvent s’y brancher sans imposer une nouvelle interface.

## Ce que l’IA ne doit pas faire

Un système comme Hermes Kanban ne doit pas donner aux agents une autonomie vague.

Les règles doivent être explicites :

- ne pas marquer une tâche Done sans vérification ;
- ne pas inventer un résultat ;
- ne pas cacher un blocage ;
- ne pas continuer si le scope devient ambigu ;
- ne pas effectuer une action irréversible sans validation ;
- ne pas traiter une correction humaine comme une suggestion faible ;
- ne pas écraser le travail d’un autre worker.

C’est pour ça que Planka est utile : le workflow rend ces règles visibles.

## Ce qu’on apprend en pratique

Plusieurs patterns émergent.

Le premier : une carte mal écrite produit un mauvais run agentique. Si l’objectif est flou, l’agent improvise. Le cadrage devient donc un vrai travail.

Le deuxième : les commentaires courts valent mieux que les longs romans. Un heartbeat utile doit dire ce qui a été fait, ce qui bloque, et ce qui vient ensuite.

Le troisième : les agents doivent bloquer vite. Un agent qui tourne en rond pendant une heure est pire qu’un agent qui dit au bout de deux minutes : “il me manque tel credential”.

Le quatrième : la vérification doit être séparée de l’exécution. Un worker peut dire “j’ai corrigé”. Hermes doit vérifier.

Le cinquième : les humains doivent pouvoir reprendre à tout moment. Si le board n’est compréhensible que par l’agent qui l’a rempli, le système a échoué.

## Vers un gestionnaire de todo vraiment mixte

Le potentiel dépasse largement le simple kanban.

Un vrai gestionnaire de travail hybride pourrait gérer :

- des tâches humaines ;
- des tâches agentiques ;
- des tâches semi-automatiques ;
- des validations ;
- des dépendances ;
- des permissions ;
- des budgets ;
- des modèles spécialisés ;
- des workers locaux ou cloud ;
- des preuves de vérification ;
- des handoffs propres.

Planka + Hermes Kanban est une façon pragmatique d’explorer cette direction sans repartir de zéro.

Planka fournit l’interface et l’état.

Hermes fournit l’orchestration.

Les modèles fournissent les capacités d’exécution.

Les humains gardent la stratégie, la validation et le jugement.

## Conclusion

Le futur de la todo list n’est probablement pas une todo list avec un bouton “Ask AI”.

C’est un système où les humains et les agents partagent le même espace de travail.

Les cartes ne sont plus seulement des rappels. Elles deviennent des contrats exécutables. Les colonnes ne sont plus seulement visuelles. Elles deviennent un protocole d’orchestration. Les commentaires ne sont plus seulement des notes. Ils deviennent un journal d’exécution.

Planka + Hermes Kanban nous sert de prototype pour ça : un gestionnaire de travail mixte, où l’IA ne vit pas à côté du projet, mais dedans.

Pas comme un collègue magique. Comme un worker traçable, contrôlé, vérifiable, et utile.
