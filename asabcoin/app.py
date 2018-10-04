import os
import uuid
import aiohttp.web

import asab
import asab.web.rest

from .blockchain import Blockchain
from .websocket import WebSocketFactory

class AsabCoinApplication(asab.Application):


	async def initialize(self):
		self.AdminToken = None

		# Load the web service module
		from asab.web import Module
		self.add_module(Module)

		# Load the mom service module
		from asab.mom import Module
		self.add_module(Module)

		# Locate web service
		websvc = self.get_service("asab.WebService")

		# Be rest!
		websvc.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		websvc.WebApp.router.add_get(r'/api/{blockchain}', self.download)
		websvc.WebApp.router.add_put(r'/api/{blockchain}', self.upload)
		websvc.WebApp.router.add_get(r'/api/{blockchain}/actuals', self.actuals)
		websvc.WebApp.router.add_get(r'/api/{blockchain}/state', self.state)
		websvc.WebApp.router.add_put(r'/api/{blockchain}/params', self.set_params)
		websvc.WebApp.router.add_get(r'/api/{blockchain}/txpool', self.txpool)

		# Add a websocket handler
		self.WebSocketFactory = WebSocketFactory(self)
		websvc.WebApp.router.add_get('/api/{blockchain}/ws', self.WebSocketFactory)

		asab.web.StaticDirProvider(websvc.WebApp, '/', os.environ.get('WEBAPPDIR', './webui'))

		# Prepare a message broker
		from asab.mom.amqp import AMQPBroker
		self.Broker = AMQPBroker(self, config={
			'url': 'amqp://guest:guest@localhost/',
			'exchange': 'amq.topic',
		})

		# Initialize the blockchain(s)
		self.Blockchains = {
			'coingame': Blockchain(self, './gamecoin.yaml', difficulty=22)
		}

		self.PubSub.subscribe("Application.tick/60!", self.new_admin_token)


	async def main(self):
		print("Ready.")
		self.new_admin_token()


	async def actuals(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		actuals = {}
		for block in blockchain:
			credit = actuals.get(block.Miner, 0.0)
			for transaction in block.Transactions:
				credit += transaction.Fee
			actuals[block.Miner] = credit

		return asab.web.rest.json_response(request, data=actuals)


	async def download(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		if request.headers.get("Accept") == 'text/json':
			# We suppose to return JSON variant of the blockchain
			bc = []
			for block in blockchain:
				bc.append({
					'Timestamp': block.Timestamp.isoformat(),
					'Difficulty': block.Difficulty,
					'Nonce': block.Nonce,
					'Miner': block.Miner,
					'TransactionCount': len(block.Transactions),
				})
			return asab.web.rest.json_response(request, data=bc)

		resp = aiohttp.web.StreamResponse(
			status=200, 
			reason='OK', 
			headers={'Content-Type': 'text/yaml'},
		)

		await resp.prepare(request)

		f = open(blockchain.Filename, 'rb')
		while True:
			buffer = f.read(4096)
			if len(buffer) == 0:
				await resp.drain()
				break

			await resp.write(buffer)

		return resp


	async def state(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		return asab.web.rest.json_response(request, data={
			'Digest': blockchain.LastDigest,
			'Difficulty': blockchain.Difficulty,
			'Fee': blockchain.MiningFee,
		})


	async def upload(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		try:
			blockchain.append(await request.read())
		except Exception as e:
			return asab.web.rest.json_response(request, status=400, data={
				'result': 'FAILED',
				'message': str(e),
			})

		return asab.web.rest.json_response(request, data={'result': 'OK'})


	async def txpool(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		if request.headers.get("Accept") == 'text/json':
			# We suppose to return JSON variant of the blockchain
			txs = []
			for tx in blockchain.TransactionPool.Transactions.values():
				txs.append({
					'Id': str(tx.Id),
					'Fee': tx.Fee,
				})
			return asab.web.rest.json_response(request, data=txs)


		resp = aiohttp.web.StreamResponse(
			status=200, 
			reason='OK', 
			headers={'Content-Type': 'text/yaml'},
		)

		await resp.prepare(request)

		for tx in blockchain.TransactionPool.Transactions.values():
			await resp.write(b'--- ')
			await resp.write(tx.yaml_dump().encode('utf-8'))
		await resp.drain()

		return resp


	async def set_params(self, request):
		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		a = request.headers.get("Authorization")
		if a is None:
			raise aiohttp.web.HTTPUnauthorized(headers={
				'WWW-Authenticate': 'Bearer realm="CoinGame"'
			})

		try:
			a = a.split(' ', 2)
			if a[0] != 'Bearer':
				raise aiohttp.web.HTTPUnauthorized(headers={
					'WWW-Authenticate': 'Bearer realm="CoinGame"'
				})

			if a[1] != self.AdminToken or self.AdminToken is None:
				raise aiohttp.web.HTTPUnauthorized(headers={
					'WWW-Authenticate': 'Bearer realm="CoinGame"'
				})

		except:
			raise aiohttp.web.HTTPUnauthorized(headers={
				'WWW-Authenticate': 'Bearer realm="CoinGame"'
			})

		# Authentication / Authorization done

		rbody = await request.json()
		for k, v in rbody.items():
			if k == 'Difficulty':
				v = int(v)
				assert(v>=0)
				assert(v<400)
				blockchain.set_diffuculty(v)
			else:
				L.error("Unknown parameter '{}' (value:'{}'') received".format(k, v))


		return asab.web.rest.json_response(request, data={'result': 'OK'})


	def new_admin_token(self, event_type=None):
		self.AdminToken = uuid.uuid4().hex
		print("Admin token:", self.AdminToken)

