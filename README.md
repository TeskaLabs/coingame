# Welcome to the CoinGame!

A fun game for coders that illustrates the usage of asynchronous Python via the blockchain mining.
It is a teaching tool for demonstrating principles of distributes computing, microservices, asynchronous programming, and many other modern software engineering principles.
The CoinGame is loosely based on the BitCoin and blockchain technology.
The CoinGame is designed for a Python, but players may use other programming languages as well.

## Rules

The goal of this game is to mine more coins than the other players.
A player needs to implement a code that finds a new block and adds it to a blockchain.
When the player submits a new valid block to a blockchain, he collects a miner reward and fees from each transaction that he decided to add to a block.
The player who gains the most coins at the end of the game wins.

The player can be a single coder or a team.

Players agree at the beginning of the game on how many mining computers they will use.
The computing performance should be evenly distributed across players since this is game about software engineering skills and not about a raw power of the hardware.
Specialised mining hardware such as ASIC is not allowed in the game unless all players agree.

The game lasts approximately 3 hours.
The time of the end of the game is defined at the beginning of the game, and it is known to players.
The game can be prolonged during the game if all players agree.

## CoinGame server

The game is provided by a CoinGame server (named `coingamesvr.py`).
You find this server in the GitHub repository.
This server provides an HTTP REST interface and also publishes various messages over RabbitMQ / AMQP. 
A player can decide what interface (HTTP REST, RabbitMQ or both) she or he needs for mining.
The server manages a blockchain and a pool of transactions.

## The game

The game starts with a first block pre-mined by a game provider.
All players have zero coins (aka Score) at the beginning.
Each player starts to implement his mining code from scratch.
The mining code is about constructing a valid block of transactions with a proper hash.
At one point in time, each player starts to execute their code and hence starts to mine blocks.
Players use CoinGame REST API and/or messages publishes via RabbitMQ to build a valid block and to submit that block to a CoinGame server.
Whenever a server accepts a valid block, a relevant player receives a reward based on the mining reward and fees from each transaction.
The CoinGame server adds a reward to a player score.

Later in the game, players run their mining code, and they can decide if they want to optimize, refactor or change their code to improve their changes.


## Prerequisites

 * Internet connectivity or at least a LAN with an IP protocol (e.g., on the off-site)
 * Laptops or PCs for each player, they should be comparable concerning computing performance.
 * Python (or other) runtime environment at each player laptop
 * Text editor or IDE at each player laptop
 * Coin Game Server
 * RabbitMQ 

