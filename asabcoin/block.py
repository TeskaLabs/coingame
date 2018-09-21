import yaml
import datetime
import re

from .transaction import Transaction

class Block(yaml.YAMLObject):
	yaml_tag = u'!Block'

	miner_re = re.compile(r'^[0-9a-zA-Z]{3,32}$')

	def __repr__(self):
		return "%s(Timestamp=%r, Difficulty=%r, Nonce=%r, Miner=%r, Transactions=[%d])" % (
			self.__class__.__name__,
			self.Timestamp.isoformat(),
			self.Difficulty,
			self.Nonce,
			self.Miner,
			len(self.Transactions),
		)

	def validate(self):
		if not hasattr(self, 'Timestamp'):
			raise RuntimeError("No 'Timestamp' attribute.")
		if not isinstance(self.Timestamp, datetime.datetime):
			raise RuntimeError("'Timestamp' has to be a Date & Time.")

		if not hasattr(self, 'Difficulty'):
			raise RuntimeError("No 'Difficulty' attribute.")
		if not isinstance(self.Difficulty, int):
			raise RuntimeError("'Difficulty' has to be an Integer.")
		if self.Difficulty <= 0:
			raise RuntimeError("'Difficulty' has to be a positive Integer.")
		if self.Difficulty > 384:
			raise RuntimeError("'Difficulty' is too large.")

		if not hasattr(self, 'Nonce'):
			raise RuntimeError("No 'Nonce' attribute.")
		if not isinstance(self.Nonce, int):
			raise RuntimeError("'Nonce' has to be an Integer.")

		if not hasattr(self, 'Miner'):
			raise RuntimeError("No 'Miner' attribute.")
		if not isinstance(self.Miner, str):
			raise RuntimeError("'Miner' has to be a String.")
		if len(self.Miner) < 3:
			raise RuntimeError("'Miner' length must be at least 3.")
		if len(self.Miner) > 32:
			raise RuntimeError("'Miner' length must be at maximum 32.")
		if self.miner_re.match(self.Miner) is None:
			raise RuntimeError("'Miner: {}' has an incorrect format.".format(self.Miner))

		if not hasattr(self, 'Transactions'):
			raise RuntimeError("No 'Transactions' attribute.")
		if not isinstance(self.Transactions, list):
			raise RuntimeError("'Transactions' has to be a list.")
		if len(self.Transactions) <= 0:
			raise RuntimeError("'Transactions' has to contain at least 1 transaction.")
		if len(self.Transactions) > 1000:
			raise RuntimeError("'Transactions' has to contain at most 1000 transactions.")

		txids = set()
		for transaction in self.Transactions:
			if not isinstance(transaction, Transaction):
				raise RuntimeError("Transaction elements must be of the type Transaction (is {}).".format(type(transaction)))
			transaction.validate()
			if transaction.Id in txids:
				raise RuntimeError("Transaction ID {} is not unique.".format(transaction.Id))

		keys = set(self.__dict__.keys())
		keys.remove('Timestamp')
		keys.remove('Difficulty')
		keys.remove('Nonce')
		keys.remove('Miner')
		keys.remove('Transactions')
		if len(keys) > 0:
			raise RuntimeError("Unknown attributes provided: {}".format(', '.join(keys)))
