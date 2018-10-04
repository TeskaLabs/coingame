def format_block(prev_hash, difficulty, fee, nonce, miner, transactions):
	timestamp = datetime.datetime.utcnow().isoformat()
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
""".format(prev_hash=prev_hash, difficulty=difficulty, timestamp=timestamp, fee=fee, nonce=nonce, miner=miner)
	
	for tx in transactions:
		# Remove the 'ValidTo' line from transaction.
		tx = re.sub(r'\nValidTo: .*\n', '\n', tx, re.M)
		block += '  - ' + tx[4:].replace('\n', '\n    ')[:-4]

	return block