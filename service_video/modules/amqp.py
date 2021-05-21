import asyncio
import json
import os

import aioamqp


async def send(body, queue):
    transport, protocol = await aioamqp.connect(host=os.environ.get('RABBITMQ_HOST'),
                                                port=5672,
                                                login=os.environ.get('RABBITMQ_DEFAULT_USER'),
                                                password=os.environ.get('RABBITMQ_DEFAULT_PASS'))
    channel = await protocol.channel()

    if 'DEBUG' in os.environ:
        await channel.queue_declare(queue, durable=True)
    else:
        await channel.queue_declare(queue)
    await channel.basic_publish(json.dumps(body), '', queue)
    await protocol.close()
    transport.close()


loop = asyncio.get_event_loop()
