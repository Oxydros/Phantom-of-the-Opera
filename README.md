# AI: Phantom of The Opera

## Introduction

This is a school project for the Artificial Intelligence course.  
The aim is to create two AIs that will play the **Detective** and the **Phantom** for the board game [Phantom of the Opera](https://boardgamegeek.com/boardgame/29910/phantom-opera-mystery-game).  
In the end, all the AI of course's student will compete against each other to determine which one is the best.  
  
We **HAD** to comply to the server located in this repository: https://github.com/groznyniko/ia_fopera.  
  
_We are french developers, and we mostly called the Phantom as Ghost inside our code. Sorry :)_

## Algorithms

We had two main goals doing this project: learn about AI, and win the tournament.  
We did two algorithm:
- **AlphaBeta**
- Reinforcment learning using **Deep Q-Network**. We inspired ourselves from the paper [Playing Atari with Deep Reinforcement Learning](https://arxiv.org/pdf/1312.5602.pdf)

## Installation

### Libraries

You need to have installed Python 3.7 and PyTorch v0.4.1 or superior.  
_You may have a warning, look here https://discuss.pytorch.org/t/about-pytorch-update/476_

### Launch it

You can find 4 `dummy.py` files:
- Dummy0 and Dummy1 are the Detective and Phantom agents using the **DQN**
- Dummy2 and Dummy3 are the Detective and Phantom agents using the **Alpha Beta**
  
Communication between the clients and the server is inside the `runner.py` or `runnerSocket.py`.  
By default, all the dummies use the `runner.py`.  
  
There is two different servers:
- `fantome_opera_serveur.py` uses files to communicate with the clients. Use `runner.py`(default) in your dummies.  
- `fantome_opera_serveur_socket.py` uses sockets to communicate with the clients. It's by far the best way to test this project. To do so, you need to use the `runnerSocket` inside the dummies, instead of the basic `runner`.

_Default is file communication, because the professor wanted it that way._

### Contact

Oïhan CAILLAUD (@ourdin)
Louis VENTRE (@oxydros)
