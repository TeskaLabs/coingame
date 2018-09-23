import logging
import hashlib
import asyncio
import yaml
import os
import io

from .blockchainfile import iterate_blockchainfile
from .block import Block
from .hash import Hash
from .difficulty import calculate_difficulty
from .txpool import TransactionPool

#

L = logging.getLogger(__name__)

#

def parse(inp, exp_class):
	obj = yaml.load(inp)
	if not isinstance(obj, exp_class):
		raise RuntimeError("Expected {} got {}".format(exp_class, obj.__class__.__name__))
	obj.validate()
	return obj


class Blockchain(object):


	def __init__(self, app, fname, difficulty=20):
		self.Filename = fname
		self.LastDigest = None
		self.Difficulty = difficulty
		self.MiningFee = 1.0
		self.Broker = app.Broker
		self.Loop = app.Loop

		self.TransactionPool = TransactionPool(app)
		self.Blocks = None

		if not os.path.isfile(self.Filename):
			self.initialize("""--- !Hash
Digest: '000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
--- !Block
Timestamp: 2018-09-16T23:32:56.095486Z
Difficulty: 32
Nonce: 77726441
Miner: TeskaLabs
Transactions:
  - !Transaction
    Fee: 1.0
--- !Hash
Digest: '00000000b9d0b0ceeee295cb2c02387d16ecf3b52a0811f165e5902ef78659db96e409b9493ba7fe4433e2439f5672a7'
""")
		else:
			self.load()


	def initialize(self, first_block):
		if os.path.isfile(self.Filename):
			raise RuntimeError("Blockchain {} already exists".format(self.Filename))

		open(self.Filename, 'wb').write(first_block.encode('utf-8'))

		self.load()


	def __iter__(self):
		return iter(self.Blocks)

	def load(self):
		self.Blocks = []

		try:
			bci = iterate_blockchainfile(open(self.Filename, 'rb'))
		except FileNotFoundError:
			L.warn("The blockchain {} is empty. Initialize it with a first block!".format(self.Filename))
			return			
		try:
			bhash = next(bci) # First hash
		except StopIteration:
			L.warn("The blockchain {} is empty. Initialize it with a first block!".format(self.Filename))
			return

		bhash_obj = parse(bhash, Hash)

		while True:
			# Read a block
			try:
				block = next(bci)
			except StopIteration:
				break
			block_obj = parse(block, Block)

			m = hashlib.sha384()
			m.update(bhash)
			m.update(block)
			m.update(bhash)
			m.update(block)

			# Read a hash
			bhash = next(bci)
			bhash_obj = parse(bhash, Hash)

			if m.hexdigest() != bhash_obj.Digest:
				raise RuntimeError("Digest of the block doesn't match ({} != {})".format(exp_digest, bhash_obj.Digest))

			exp_difficulty = calculate_difficulty(m)
			if exp_difficulty < block_obj.Difficulty:
				raise RuntimeError("Calculated difficulty is lower than advertised.")

			self.Blocks.append(block_obj)

		self.LastDigest = bhash_obj.Digest


	def append(self, block_data):
		if not block_data.startswith(b'--- !Hash\n'):
			raise RuntimeError("Expecting a hash and a block in YAML.")

		m = hashlib.sha384()
		m.update(block_data)
		m.update(block_data)
		block_difficulty = calculate_difficulty(m)
		if block_difficulty < self.Difficulty:
			raise RuntimeError("The block difficulty is too low.")

		bci = iterate_blockchainfile(io.BytesIO(block_data))
		
		prev_hash = parse(next(bci), Hash)
		if prev_hash.Digest != self.LastDigest:
			raise RuntimeError("The hash is not matching the lastest hash in the blockchain.")

		block = parse(next(bci), Block)
		if len(block.Transactions) < 5:
			raise RuntimeError("The block has to contain at least 5 transactions.")

		# Ensure that we are at the end ...
		try:
			parse(next(bci), Block)
		except StopIteration:
			pass

		# Ensure that transactions matches ones in the pool
		for n, tx in enumerate(block.Transactions):
			if n == 0:
				#Validate that a first transaction doesn't have ID (mining transaction)		
				if tx.Id is not None:
					raise RuntimeError("The first (mining) transaction in the block cannot have an Id.")
				#Validate that a mining transactaction has Fee of max. value defined by the pool
				if tx.Fee > self.MiningFee:
					raise RuntimeError("The mining fee is above {}.".format(self.MiningFee))
			else:
				#Validate that rest of transactions are not mining transaction
				if tx.Id is None:
					raise RuntimeError("More than one mining transaction found in the list.")

				otx = self.TransactionPool.get(tx.Id)
				if otx is None:
					raise RuntimeError("Transaction from a block is not in the pool.")

				if otx != tx:
					raise RuntimeError("Transaction doesn't match.")

		# Remove transactions from a pool
		for tx in block.Transactions[1:]:
			self.TransactionPool.pop(tx.Id)


		# Append the block to a chain
		i = block_data.find(b'\n--- !Block\n')
		open(self.Filename, 'ab').write(
			block_data[i+1:]
			+ "--- !Hash\nDigest: '{}'\n".format(m.hexdigest()).encode('utf-8')
		)

		self.load()

		msg = yaml.dump(block, explicit_start=True)
		asyncio.ensure_future(
			self.Broker.publish(
				msg,
				target="block.added",
				content_type="text/yaml",
			),
			loop = self.Loop,
		)
