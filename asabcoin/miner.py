import yaml

import random
import hashlib
import datetime

from .difficulty import calculate_difficulty

def miner(
		difficulty:int = 16,
		prev_hash:str='000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
		miner:str='TeskaLabs',
		transactions=None,
		fee=1.0,
	):
	random.seed()
	max_lz = 0

	cycle_counter = 0
	while 1:
		nonce = random.randint(0, 100000000)
		now = datetime.datetime.utcnow().isoformat()
		block = """--- !Hash
Digest: '{prev_hash}'
--- !Block
Timestamp: {timestamp}Z
Difficulty: {difficulty}
Nonce: {nonce}
Miner: {miner}
Transactions:
  - !Transaction
    Fee: {fee}
""".format(
		prev_hash = prev_hash,
		timestamp=now,
		difficulty=difficulty,
		nonce=nonce,
		miner=miner,
		fee=fee,
	)

		if transactions is not None:
			for transaction in transactions:
				block += """  - !Transaction
    Id: {txid}
    Fee: {fee}
    Data: !!binary |
      RWhFaEVoRWg=
""".format(
		txid=transaction.Id,
		fee=transaction.Fee,
		#TODO: Data
	)

		blockbytes = block.encode('utf-8')
		m = hashlib.sha384()
		m.update(blockbytes)
		m.update(blockbytes)

		# Calculate difficulty (a number of leading zeroes)
		cacl_diff = calculate_difficulty(m)
		
		max_lz = max(max_lz, cacl_diff)

		if cacl_diff < difficulty:
			cycle_counter += 1
			# if (cycle_counter % 100000) == 0:
			# 	print("Cycle {}, max LZ: {}".format(
			# 		cycle_counter,
			# 		max_lz,
			# 	))
			# 	max_lz = 0
			continue

		return block+"--- !Hash\nDigest: '{}'\n".format(m.hexdigest())
