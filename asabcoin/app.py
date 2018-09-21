import aiohttp.web

import asab
import asab.web.rest

from .blockchain import Blockchain
from .miner import miner

class AsabCoinApplication(asab.Application):


	async def initialize(self):

		# Load the web service module
		from asab.web import Module
		self.add_module(Module)

		# Load the mom service module
		from asab.mom import Module
		self.add_module(Module)

		# Load the proactor service module
		from asab.proactor import Module
		self.add_module(Module)

		# Locate web service
		websvc = self.get_service("asab.WebService")

		# Be rest!
		websvc.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)
		websvc.WebApp.router.add_get(r'/', self.homepage)

		websvc.WebApp.router.add_get(r'/{blockchain}', self.download)
		websvc.WebApp.router.add_put(r'/{blockchain}', self.upload)
		websvc.WebApp.router.add_get(r'/{blockchain}/actuals', self.actuals)
		websvc.WebApp.router.add_put(r'/{blockchain}/init', self.init)
		websvc.WebApp.router.add_get(r'/{blockchain}/state', self.state)

		# Prepare a message broker
		from asab.mom.amqp import AMQPBroker
		self.Broker = AMQPBroker(self, config={
			'url': 'amqp://guest:guest@localhost/',
			'exchange': 'asabcoin.exchange',
		})

		# Initialize the blockchain(s)
		self.Blockchains = {
			'heurekacoin': Blockchain(self, './blockchain.yaml', difficulty=16)
		}



	async def homepage(self, request):
		return asab.web.rest.json_response(request, data={
			'title': 'AsabCoin',
			'vendor': 'TeskaLabs Ltd',
		}, pretty=True)


	async def init(self, request):
		req = await request.json()
		difficulty = int(req.get('difficulty', 16))

		blockchain = self.Blockchains.get(request.match_info['blockchain'])
		if blockchain is None:
			raise aiohttp.web.HTTPNotFound()

		proactor = self.get_service("asab.ProactorService")
		#TODO: Allow to specify a miner
		def mine_first_block():
			return miner(difficulty=difficulty)
		first_block = await proactor.run(mine_first_block)

		blockchain.initialize(first_block)

		return asab.web.rest.json_response(request, data={'result': 'OK'})


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

		blockchain.append(await request.read())

		return asab.web.rest.json_response(request, data={'result': 'OK'})
