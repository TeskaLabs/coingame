
def iterate_blockchainfile(f):
	'''
	Read a YAML blockchain file and split it into documents.
	'''
	latch = b''
	while True:
		b = f.read(1)
		if len(b) == 0: break
		latch += b
		if latch[-5:] == b'\n--- ':
			yield(latch[:-4])
			latch = b'--- '
	if len(latch) > 0:
		yield(latch)
