# IA_Fantom_of_The_Opera

## Reinforcement learning using QLearning

### 2 Agents

* Fantom
* Detective

### 3 questions to answer to

* Selection of colors, noted E0
* Selection of Power, noted E1
* Selection of Deplacement, noted E2

When we talk about all of this questions, we will use the E* notation.

### Data

We can find different type of informations, defining the state:
* Position of the colors (room they are in) -> **D0** *88 data points*
* Position of the lock -> **D1** *2 data points*
* Position of the light -> **D2** *1 data point*
* Score of the game -> **D3** *1 data point*
* Color of the fantom -> **D4** *1 data point*
* Was the agent the first one of the "tour" -> **D5** *1 data point*
* 4 selected colors to play -> **D6** *4 data points*
* Color choosed to be played -> **D7** *1 data point*

|    | D0 | D1 | D2 | D3 | D4 | D5 | D6 | D7 | Size |
|----|----|----|----|----|----|----|----|----|------|
| E0 | X  | X  | X  | X  | X  | X  |    |    | 106  |
| E1 | X  | X  | X  | X  | X  | X  |    | X  | 107  |
| E2 | X  | X  | X  | X  | X  | X  |    | X  | 107  |

## Realisation

* 1 neural network for each question
* Reward is calculated at the end of the "half turn" and propagated back to the 3 neural net

### Neural Net E0

* Size of entry 107  
* Size of exit 8 (colors)

### Neural Net E1

* Size of entry 105  
* Size of exit 2 (yes or no)

### Neural Net E2

* Size of entry 105  
* Size of exit 9 (9 rooms)

## V2 data

Nous considérons chaque action du jeu comme un bouton sur un controleur.  
L'agent va apprendre qu'en fonction de certains état du jeu des boutons sont plus  
utiles que d'autre.  
  
Differents choix possibles au cours du jeu (actions):
* Choix d'une couleur (8 couleurs => 8 actions)
* Nouvelle position de la couleur actuelle (10 salles => 10 actions)
* Choix d'utiliser le pouvoir de la couleur actuelle (Oui ou Non => 2 actions)

Le nombre d'actions est donc de **20**

On peut remarque que une couleur actuelle est nécessaire dans l'etat du jeu.    
  
On peut identifier différentes étapes uniques au cours du jeu, qui se relaient de façon cyclique:  
* Sélection d'une carte
* Pouvoir Oui/Non
* Déplacement
  
Basé sur ces observations, on peut déterminer les informations requises dans le state du jeu:
* Position des couleurs => 8 integer ayant une valeur de 0 à 9, représentant la salle dans laquelle ils sont
* L'état d'innoncence des couleurs => 8 entiers, ayant pour valeur 0 si ils sont suspects ou 1 si ils sont innocents
* Position du locker => 2 integer ayant une valeur de 0 à 9, indiquant le chemin bloqué entre deux salles
* Position de la salle noir => 1 integer ayant une valeur de 0 à 9, indiquant quelle salle est sombre
* Le score du jeu => 1 entier ayant une valeur > 0
* La couleur selectionnée => 1 entier ayant une valeur comprise entre 0 et 8, représentant la couleur actuelle à jouer
* L'état du jeu => 1 entier ayant une valeur >= 0 et <= 2 représentant les différents états cités plus haut
  
Seulement pour le fantome: 
* Le numéros de la couleur fantome

La taille de la data est donc de:
* **22** pour le detective
* **23** pour le ghost

## Links

https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

