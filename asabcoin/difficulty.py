def calculate_difficulty(hashobj):
	difficulty = 0
	for b in hashobj.digest():
		if (b & 0x80) == 0x80: return difficulty
		difficulty += 1
		if (b & 0x40) == 0x40: return difficulty
		difficulty += 1
		if (b & 0x20) == 0x20: return difficulty
		difficulty += 1
		if (b & 0x10) == 0x10: return difficulty
		difficulty += 1
		if (b & 0x08) == 0x08: return difficulty
		difficulty += 1
		if (b & 0x04) == 0x04: return difficulty
		difficulty += 1
		if (b & 0x02) == 0x02: return difficulty
		difficulty += 1
		if (b & 0x01) == 0x01: return difficulty
		difficulty += 1
	return difficulty
