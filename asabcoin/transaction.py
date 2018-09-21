import yaml
import datetime

class Transaction(yaml.YAMLObject):
	yaml_tag = u'!Transaction'


	def __init__(self, txid:int, fee:float, data:bytes, validto:datetime.datetime=None):
		self.Id = txid
		self.Fee = fee
		self.Data = data
		if validto is not None:
			self.ValidTo = validto # This one is only used for unconfirmed transactions, waiting to be added to a blockchain


	def __eq__(self, other_tx):
		return self.Id == other_tx.Id


	def __hash__(self):
		return hash(self.Id)


	def __repr__(self):
		attrs=["{}={}".format(attr, getattr(self, attr)) for attr in ['Id', 'Fee', 'Data', 'ValidTo'] if hasattr(self, attr)]
		return "{}({})".format(self.__class__.__name__, ", ".join(attrs))


	def prepare(self):
		return Transaction(
			txid=self.Id,
			fee=self.Fee,
			data=self.Data
		)


	def validate(self):
		if hasattr(self, 'Id'):
			if not isinstance(self.Id, int):
				raise RuntimeError("'Id' has to be an Integer.")
			if self.Id <= 0:
				raise RuntimeError("'Id' has to be a positive Integer.")
		else:
			self.Id = None

		if not hasattr(self, 'Fee'):
			raise RuntimeError("No 'Fee' attribute.")
		if not isinstance(self.Fee, float):
			raise RuntimeError("'Fee' has to be an Float.")
		if self.Fee <= 0.0:
			raise RuntimeError("'Fee' has to be a positive float.")

		keys = set(self.__dict__.keys())
		if 'Id' in keys: keys.remove('Id')
		keys.remove('Fee')
		if 'Data' in keys: keys.remove('Data')
		if len(keys) > 0:
			raise RuntimeError("Unknown attributes provided: {}".format(', '.join(keys)))
