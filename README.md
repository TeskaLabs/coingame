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
Once the transaction is added to a blockchain as part of the valid block, the CoinGame server removes this transaction from a pool, so it is not available for other players.
It means that each transaction can be present in the blockchain only once.
A server rejects any subsequent block - even if it otherwise is valid - because the given transaction has been already included in the blockchain.

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

 * Internet connectivity or a LAN with an IP protocol (e.g., on the retreat site)
 * Laptop or PC for each player (comparable concerning computing performance)
 * Python (or other) runtime environment at each player laptop or PC
 * Text editor or IDE at each player laptop or PC
 * CoinGame Server
 * RabbitMQ 

## Blockchain

The blockchain is a YAML file, that consist of the series of two documents: a block and a hash.
The actual blockchain can be downloaded from the REST API of the CoinServer.

![Blockchain diagram](https://raw.githubusercontent.com/TeskaLabs/coingame/master/docs/blockchain.jpg)

The blockchain starts with a first block, that is pre-mined by a TeskaLabs.
Players add their blocks after the last block in the blockchain.

## The block

The block consists of block attributes and a list of transactions.

### Block attributes

 * `Timestamp` contains a UTC date and time of a block creation in format defined by ISO 8601  
    (aka `YYYY-MM-DDThh:mm:ss.uuuuuuZ`).
 * `Difficulty` is an positive integer number.
    It is in the range between 1 and 384.
    The difficulty for a new block is provided by a CoinGame server.
 * `Nonce` is the random integer number selected by a miner.
 * `Miner` is a string that cointains a name of the player who mined this block.  
    The format is defined by regex `^[0-9a-zA-Z]{3,32}$`.

## Transactions

Each block contains a list of transactions.
The list must contain at least 5 transactions (the exception is the first block with one transaction only).
The maximum number of transactions in the block is 1000.

The first transaction must a mining reward transaction, which contains only a miner reward in the `Fee` attribute.
The CoinServer provides a maximum miner fee value.

Transaction attributes:

 * `Id` is a long integer that identifies the transaction uniquely in the transaction pool.
 * `Fee` a float that specifies a fee for a miner for including this transaction in the block.
 * `Data` is a binary field in a Base64 encoding that contains additional details about the transaction.

A `ValidTo` timestamp limits each transaction durability.
If the transaction is not added to a blockchain till `ValidTo` time, it is discarded and must not be used any longer.
A `ValidTo` attribute exists only for transactions that are yet in the pool this attribute must be removed when the transaction is added to a block.

