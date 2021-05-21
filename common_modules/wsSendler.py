import json
import os
import ssl

import websocket


class WebSocket:
    def __init__(self):
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE, 'ssl_version': ssl.PROTOCOL_TLSv1_2})

    def sendSocket(self, jwt, msg):
        self._connect()
        self.ws.send(json.dumps({'jwt': jwt, 'msg': msg}))
        self._close()

    def _connect(self):
        self.ws.connect(os.environ.get('WEBSOCKET_HOST'))

    def _close(self):
        self.ws.close()
