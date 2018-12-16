# IA_Fantom_of_The_Opera

## Installation

Ce programme nécessite pytorch et python 3.7

## 2 Agents

* Fantom
* Detective

## 2 IA

Nous avons développé ces 2 agents suivant 2 types d'algorithmes: Alpha-Beta et Deep QLearning (DQN).  
Les dummy0 et dummy1 sont nos 2 IA rendu pour ce module.  
En effet, après différents tests, il se trouve que l'alpha-beta est plus fort que le DQN mais le temps de calcul est bcp  
trop long entre chaque coup. La latence du serveur état de 0.01, notre agent n'a pas le temps de prendre une décision.  

Nous soumettons donc dans ces 2 dummies les agents basés sur le DQN. La encore la latence du serveur, qui est de 0.01 par default  
nous empêche de temps en temsp de répondre dans les temps, décalant alors tout nos réponses pour les questions suivantes.  
  
Monter la latence du serveur à 0.1 devrait résoudre le problème.  

## Définition d'un état du jeu et des questions possibles

Nous considérons chaque action du jeu comme un bouton sur un controleur.  
L'agent va apprendre qu'en fonction de certains état du jeu des boutons sont plus  
utiles que d'autre.  
  
Differents choix possibles au cours du jeu (actions):
* Choix d'une couleur (8 couleurs => 8 actions)
* Choix d'une position (10 salles => 10 actions)
* Choix d'utiliser un pouvoir (Oui ou Non => 2 actions)

Le nombre d'actions est donc de **20**

On peut remarque que une couleur actuelle est nécessaire dans l'etat du jeu.    
  
On peut identifier différentes étapes uniques au cours du jeu, qui se relaient de façon cyclique:  
* Sélection d'une carte
* Pouvoir Oui/Non
* Déplacement
* Sélection carte pouvoir violet
* Sélection position pouvoir blanc
* Sélection position pouvoir gris
* Sélection position pouvoir bleu
  
Basé sur ces observations, on peut déterminer les informations requises dans le state du jeu:
* Position des couleurs => 8 integer ayant une valeur de 0 à 9, représentant la salle dans laquelle ils sont
* L'état d'innoncence des couleurs => 8 entiers, ayant pour valeur 0 si ils sont suspects ou 1 si ils sont innocents
* Position du locker => 2 integer ayant une valeur de 0 à 9, indiquant le chemin bloqué entre deux salles
* Position de la salle noir => 1 integer ayant une valeur de 0 à 9, indiquant quelle salle est sombre
* Le score du jeu => 1 entier ayant une valeur > 0
* La couleur selectionnée => 1 entier ayant une valeur comprise entre 0 et 8, représentant la couleur actuelle à jouer
* L'état du jeu => 1 entier ayant une valeur >= 0 et <= 6 représentant les différents états cités plus haut
  
Seulement pour le fantome: 
* Le numéros de la couleur fantome

La taille de la data est donc de:
* **22** pour le detective
* **23** pour le ghost

Gestion des states:
* Chaque question enchaine une action. Nous représentons ici une question par *q*
* Pour chaque action, on enregistre l'état *S(q)*, l'action, le reward et l'état *S+1(q)*
* L'état **S(q)** est l'état au moment de la question, il est donc trivial à obtenir
* L'état **S+1(q)** est l'état du jeu suite à l'interprétation de notre réponse par le serveur.

Nous pouvons remarquer 3 différentes façon d'obtenir cet état **S+1(q)**:
* Lors d'une nouvelle question qui suit la précédente. On a donc **S+1(q) = S(q + 1)**
* Lors d'un changement de main. Si le tour passe du fantome au detective ou vice versa, on sait que l'état actuel du jeu fait suite à la derniere action du fantome ou du detective.
* Lors du début d'un nouveau tour.

## Links
https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

