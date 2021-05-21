import asyncio
import json
import os
import ssl
import pathlib

import jwt
import websockets

from modules.logger import *
from modules.sentry_sdk import *

class Server:
    clients = set()

    async def register(self, ws: websockets.WebSocketServerProtocol):
        if ws.path == '/':
            logger.info(f"------------- New client: server")
        else:
            logger.info(f"------------- New client: front")
        self.clients.add(ws)

    async def unregister(self, ws: websockets.WebSocketServerProtocol):
        self.clients.remove(ws)
        logger.info(f"Disconnect client")

    async def send_to_clients(self, message, ws):
        if self.clients:
            for cl in self.clients:
                responce = json.loads(message)
                path = cl.path.split('/')
                serverJWT = jwt.decode(responce['jwt'], verify=False)
                clientJWT = {'email': ''}
                if path[1]:
                    clientJWT = jwt.decode(path[1], verify=False)
                    logger.info("------------ EMAIL  - ", clientJWT['email'], serverJWT['email'])
                if len(path) > 2:
                    msg = json.loads(responce['msg'])
                    if path[2] == msg['video_uuid']:
                        await cl.send(responce['msg'])
                elif clientJWT['email'] == serverJWT['email']:
                    await cl.send(responce['msg'])


    async def distribute(self, ws: websockets.WebSocketServerProtocol):
        async for message in ws:
            logger.info(f"Message: {message}. Client: {ws.path}")
            await self.send_to_clients(message, ws)

        await self.unregister(ws)

    async def ws_handler(self, ws: websockets.WebSocketServerProtocol, uri):
        await self.register(ws)
        try:
            await self.distribute(ws)
        except Exception as err:
            logger.error(f"Error: {err}")
            await self.unregister(ws)




if __name__ == '__main__':

    logger.info(f'Open WebSocket')

    ssl_context = None
    if 'DEBUG' in os.environ:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.load_cert_chain(
                pathlib.Path(__file__).with_name('fullchain.pem'),
                pathlib.Path(__file__).with_name('privkey.pem'))

    server = Server()
    start_server = websockets.serve(server.ws_handler, host='0.0.0.0', port=6002, ssl=ssl_context)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
