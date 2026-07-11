# X thread draft — Planka + Hermes Kanban

## Option A — thread complet

1/ Les agents IA n’ont pas besoin d’un énième chat.

Ils ont besoin d’un état de travail partagé avec les humains.

C’est ce qu’on explore avec Planka + Hermes Kanban : un kanban open-source qui devient la source de vérité entre humains et agents.

2/ Le problème des agents “dans le chat” :

- le contexte disparaît ;
- les décisions sont dispersées ;
- personne ne sait ce qui a été tenté ;
- les tâches longues n’ont pas d’état visible ;
- les handoffs humain ↔ IA sont flous.

Le chat est un bon input. Pas un système de coordination.

3/ Dans notre setup, Planka devient la couche d’état.

Une carte = un contrat de travail.

Elle contient l’objectif, le contexte, les contraintes, les critères d’acceptation, les commentaires d’exécution, les blocages, et les preuves de vérification.

4/ Hermes Kanban tourne derrière le board.

Il lit les cartes, découpe les tâches, choisit un worker, suit l’exécution, poste des heartbeats, bloque quand il manque une décision, vérifie le résultat, puis déplace la carte.

5/ Les workers peuvent être GPT-5.5, Grok 4.5, Composer 2.5, Codex/Cursor-style lanes, etc.

Mais le modèle n’est pas le produit.

Le produit, c’est le système de coordination autour du travail.

6/ Les colonnes deviennent un protocole opérationnel :

Backlog
To Do — Human
To Do — Agent
Worker / In Progress
Human Review
Blocked
Done

Ce n’est pas décoratif. Chaque colonne définit ce qu’un humain ou un agent peut faire ensuite.

7/ Exemple : une carte en `Human Review` veut dire :

l’agent a préparé quelque chose, mais il faut une décision humaine avant de continuer.

Déployer, merger, publier, supprimer, engager un coût : ce sont des actions qui doivent pouvoir demander validation.

8/ Les commentaires Planka deviennent le journal d’exécution.

Pas “working on it”.

Plutôt :
- fichier inspecté ;
- commande lancée ;
- erreur exacte ;
- test passé ;
- prochain step ;
- blocker précis.

C’est ce qui rend le travail auditable.

9/ Le pattern important : Hermes orchestre, les workers exécutent.

Un worker peut produire un diff ou une analyse.

Mais Hermes garde la responsabilité de vérifier, réconcilier, et déplacer la carte.

Exécution ≠ validation.

10/ Ce que ça change :

Une todo app classique dit “quoi faire”.

Un gestionnaire hybride humain/IA doit aussi dire :
- qui peut le faire ;
- avec quel contexte ;
- avec quelles permissions ;
- comment vérifier ;
- où reprendre si ça bloque.

11/ Le point le plus sous-estimé : les agents doivent bloquer vite.

Un bon agent ne force pas quand il manque un credential, une décision produit ou un scope clair.

Il déplace la carte en Blocked avec une raison actionnable.

12/ Je pense que le futur de la todo list n’est pas “une todo app avec un bouton Ask AI”.

C’est un espace de travail où humains et agents partagent le même état opérationnel.

Les cartes deviennent des contrats exécutables.

13/ Repo public avec l’analyse et le draft long :

[à remplacer par l’URL GitHub]

## Option B — post court

Les agents IA n’ont pas besoin d’un énième chat.

Ils ont besoin d’un état de travail partagé avec les humains.

On expérimente Planka + Hermes Kanban : Planka sert de source de vérité humaine, Hermes orchestre derrière, et les workers GPT-5.5/Grok 4.5/Composer 2.5 exécutent des cartes comme des contrats de travail.

Une carte contient : contexte, contraintes, critères d’acceptation, permissions, logs, blockers, preuves de vérification.

Les colonnes deviennent un protocole : To Do Agent, In Progress, Human Review, Blocked, Done.

Le point clé : Hermes orchestre, les workers exécutent, les humains gardent les décisions irréversibles.

Le futur de la todo list n’est probablement pas “Ask AI dans Trello”.

C’est un gestionnaire de travail hybride où humains et agents partagent le même état opérationnel.

Repo + article : [à remplacer]
