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


## Links

https://pytorch.org/tutorials/intermediate/reinforcement_q_learning.html

