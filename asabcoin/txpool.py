import uuid
import datetime
import asyncio

import yaml

from .transaction import Transaction

class TransactionPool(object):
	'''
	This is where unconfirmed transactions are stored
	'''

	def __init__(self, app):
		self.Transactions = {}
		self.Broker = app.Broker
		self.Loop = app.Loop

		app.PubSub.subscribe("Application.tick!", self.on_tick)


	def on_tick(self, event_name):
		print("Tick!")
		
		# Search the pool and remove obsolete transactions
		now = datetime.datetime.utcnow()
		expired_txs = []
		for txid, tx in self.Transactions.items():
			if tx.ValidTo <= now:
				expired_txs.append(txid)

		for txid in expired_txs:
			del self.Transactions[txid]

		if len(self.Transactions) < 100:
			for _ in range(5):
				tx = self.generate()
				self.add(tx)


	def get(self, transaction_id):
		return self.Transactions.get(transaction_id)


	def pop(self, transaction_id):
		return self.Transactions.pop(transaction_id)		


	def add(self, transaction):
		if transaction.Id in self.Transactions:
			raise RuntimeError("Transaction is not unique!")

		now = datetime.datetime.utcnow()
		if transaction.ValidTo <= now:
			raise RuntimeError("Transaction is expired!")

		self.Transactions[transaction.Id] = transaction
		msg = yaml.dump(transaction, explicit_start=True)

		asyncio.ensure_future(
			self.Broker.publish(
				msg,
				target="transaction",
				content_type="text/yaml",
			),
			loop = self.Loop,
		)


	def generate(self):
		'''
		Generate a random transaction
		'''
		return Transaction(
			uuid.uuid1().int,
			fee=0.1,
			validto=datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
			data= b'EhEhEhEh'
		)
