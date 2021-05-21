import ssl
import json
import websocket


class WebSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE, 'ssl_version': ssl.PROTOCOL_TLSv1_2})

    def sendSocket(self, jwt, msg):
        self._connect()
        self.ws.send(json.dumps({'jwt': jwt, 'msg': msg}))
        self._close()

    def _connect(self):
        uri = f"wss://{self.host}:{self.port}/"
        self.ws.connect(uri)

    def _close(self):
        self.ws.close()
