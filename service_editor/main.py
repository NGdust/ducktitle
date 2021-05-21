import asyncio
from threading import Thread

import aioamqp
import requests
import json
import os

from modules.editor import DrawerVideo, BuilderVideo
from modules.sentry_sdk import *

def main(body):
    print("\n\n [x] Received")
    request = json.loads(body)
    drawer = DrawerVideo(request['url_video'], request['preset'], request['captions'], request['resolution'], request['duration'])
    drawer.changeAspectRatio()
    drawer.drawSubtitle()
    editor = BuilderVideo(request['jwt_token'], request['video_uuid'], request['url_video'], request['duration'])
    resultURL = editor.build()
    if resultURL:
        print(' [x] Send update')
        data = {
            'jwt_token': request['jwt_token'],
            'video_uuid': request['video_uuid'],
            'result_url': resultURL
        }
        requests.post(os.environ.get('WEBSITE_URL') + '/video/updata/', json=data)

if __name__ == '__main__':
    QUEUE = 'edit'
    async def callback(channel, body, envelope, properties):
        task = Thread(target=main, args=(body,))
        task.start()
        await channel.basic_client_ack(delivery_tag=envelope.delivery_tag)


    async def worker():
        try:
            if 'DEBUG' in os.environ:
                await asyncio.sleep(25)
            transport, protocol = await aioamqp.connect(host=os.environ.get('RABBITMQ_HOST'),
                                                        port=5672,
                                                        login=os.environ.get('RABBITMQ_DEFAULT_USER'),
                                                        password=os.environ.get('RABBITMQ_DEFAULT_PASS'))
        except aioamqp.AmqpClosedConnection:
            print("{ -- Closed connections -- }")
            return

        channel = await protocol.channel()

        if 'DEBUG' in os.environ:
            await channel.queue_declare(QUEUE, durable=True)
        else:
            await channel.queue_declare(QUEUE)
        await channel.basic_qos(prefetch_count=4, prefetch_size=0, connection_global=False)
        await channel.basic_consume(callback, queue_name=QUEUE)


    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(worker()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
