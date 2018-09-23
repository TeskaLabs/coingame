# Welcome to the CoinGame!

A fun game for coders that illustrates the usage of asynchronous Python via the blockchain mining.
It is a teaching tool for demonstrating principles of distributes computing, microservices, asynchronous programming, and many other modern software engineering principles.
The CoinGame is loosely based on the BitCoin and blockchain technology.
The CoinGame is designed for a Python, but players may use other programming languages as well.

![Screenshot from a CoinGame](https://raw.githubusercontent.com/TeskaLabs/coingame/master/docs/screenshot.png)


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
This server provides a simple user web interface, an HTTP REST interface and also publishes various messages over RabbitMQ / AMQP. 
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

Alternatively, you can use Docker to build and run CoinGame Server including all dependencies easily.
Please refer to a relevant chapter below.


## Blockchain

The blockchain is a [YAML](http://yaml.org/spec/1.2/spec.html) file, that consist of the series of two documents: a block and a hash.
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

### Transaction attributes

 * `Id` is a long integer that identifies the transaction uniquely in the transaction pool.
 * `Fee` a float that specifies a fee for a miner for including this transaction in the block.
 * `Data` is a binary field in a Base64 encoding that contains additional details about the transaction.

A `ValidTo` timestamp limits each transaction durability.
If the transaction is not added to a blockchain till `ValidTo` time, it is discarded and must not be used any longer.
A `ValidTo` attribute exists only for transactions that are yet in the pool this attribute must be removed when the transaction is added to a block.


## The hash

The hash connects two blocks.
It must be placed after each block to proof a work that was invested into a finding a valid block (aka mining).
The hash contains a single attribute `Digest` which is a hexadecimal result of the hash function.

![Hashing diagram](https://raw.githubusercontent.com/TeskaLabs/coingame/master/docs/hashing.jpg)

The hash is computed using SHA-384 hashing function **TWICE** on a previous hash and a current block in their respective textual YAML representation.

Example of the hash computation in the Python:

    import hashlib
    m = hashlib.sha384()
    m.update(PreviousHash)
    m.update(Block)
    m.update(PreviousHash)
    m.update(Block)
    Digest = m.hexdigest()


## The difficulty

The difficulty is a measure of how difficult it is to find a hash for a block below a given value.
The CoinGame server provides a current difficulty value via its REST API.
The CoinGame server rejects blocks that declares a difficulty lower than currently declared.
The difficulty may change during the game.

The difficulty value specifies the number of zeroes in a binary representation of the hash, e.g., a difficulty 20 means that hash has to start with 20x `0` in a binary representation.
Valid blocks must have a hash that conforms a declared difficulty.

![Hashing difficulty diagram](https://raw.githubusercontent.com/TeskaLabs/coingame/master/docs/difficulty.jpg)

A reasonable value of the difficulty for a game is between 20 and 28.


## Reference documentation

### CoinGame server REST API

[Interactive API documentation](https://documenter.getpostman.com/view/2573275/RWaPsm5D)

### CoinGame server AMQP

The CoinGame server publishes messages to a RabbitMQ server, to a `amq.topic` exchange.
The player can subscribe to RabbitMQ to receive these messages using AMQP protocol.
The CoinGame uses `/` (default) RabbitMQ virtual host.

![A scheme of the AMQP messaging](https://raw.githubusercontent.com/TeskaLabs/coingame/master/docs/amqp.jpg)

#### Subscription process

A player should declare an exclusive temporary queue, named with prefix `~T` (aka `~Tmyqueue`).
This queue has to be bound to a `amq.topic`.
A player can select what types of messages he wants to consume or subscribe to all types.

 1. Declare an exclusive queue

    `channel.queue_declare(queue='~Tmyqueue', exclusive=True, auto_delete=True)`

 2. Bind th queue to an exchange

    `channel.queue_bind(queue='~Tmyqueue', exchange='amq.topic', routing_key='#')`

    A `routing_key` specifies a type of messages that you are interested in.
    Special value `#` means all message types.
    More details are here: https://www.rabbitmq.com/tutorials/tutorial-five-python.html

 3. Consume messages

    `channel.basic_consume(queue='~Tmyqueue', ...)`


#### Message type `transaction.added`

The transaction has been added to a pool.

    --- !Transaction
    Data: !!binary |
      e0Ftb3VudDogOC42LCBGcm9tOiA2NE5PM0tVVE9SQVQsIFRvOiAyMUxDUVEyM0hXMkN9Cg==
    Fee: 0.1
    Id: 199364695671660490824138862191540206604
    ValidTo: 2018-09-23 10:37:53.112603


#### Message type `transaction.removed`

The transaction has been removed from a pool.
It is no longer valid and blocks with this transaction will not be accepted by a server.

    --- !Transaction
    Data: !!binary |
      e0Ftb3VudDogOC42LCBGcm9tOiA2NE5PM0tVVE9SQVQsIFRvOiAyMUxDUVEyM0hXMkN9Cg==
    Fee: 0.1
    Id: 199364695671660490824138862191540206604
    ValidTo: 2018-09-23 10:37:53.112603


#### Message type `block.added`

The new block has been added to a blockchain.

    --- !Block
    Difficulty: 16
    Miner: Taxido
    Nonce: 24393844
    Timestamp: 2018-09-23 10:46:04.653806
    Transactions:
    - !Transaction {Fee: 1.0}
    - !Transaction
      Data: !!binary |
        e0Ftb3VudDogMTUuMywgRnJvbTogSVdNNVZJMzRISThSLCBUbzogRjVCWTFRMlpGVkdYfQo=
      Fee: 0.1
      Id: 290422523990426140188794327910770834444
    - !Transaction
      Data: !!binary |
        e0Ftb3VudDogMTkuOCwgRnJvbTogQjNDNlYzTFM3S1NHLCBUbzogMFhUVE5LUjVaOFFKfQo=
      Fee: 0.1
      Id: 290423332117683785685037782059064261644


## Docker support

You can quickly start CoinGame server in the Docker.

 1. Clone CoinGame GIT repository

 2. Build an image from a git repository:

    `docker build . -t coingame`

 3. Start a Docker container

    `docker run coingame`

The containers offers a HTTP service (API and a simple UI) on a port TCP/80 and RabbitMQ/AMQP server on a port TCP/5672.
