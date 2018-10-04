import asyncio
import asab.web

class WebSocketFactory(asab.web.WebSocketFactory):


	def __init__(self, app):
		super().__init__(app)
		self.WebSockets = set()


	async def on_request(self, request):
		ws = await super().on_request(request)
		self.WebSockets.add(ws)
		return ws


	async def publish(self, loop, type, body):
		wsc = list()
		for ws in self.WebSockets:
			wsc.append(ws.send_json({
				'type': type,
				'body': body,
			}))
		
		if len(wsc) > 0:
			asyncio.gather(*wsc, loop=loop)
