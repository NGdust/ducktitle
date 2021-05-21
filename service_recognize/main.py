import asyncio
import aioamqp
import requests
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
import os
import json
from threading import Thread
from modules.wsSendler import WebSocket

from modules.logger import *
from modules.sentry_sdk import *

websocket = WebSocket()


def recognize(storage_uri, creditionals_json=None, language_code="en-US", sample_rate_hertz=24000):
    """
    Performs synchronous speech recognition on an audio file

    Args:
      storage_uri URI for audio file in Cloud Storage, e.g. gs://[BUCKET]/[FILE]
      language_code The language of the supplied audio
      creditionals_json path to server account json file
      sample_rate_hertz Sample rate in Hertz of the audio data sent
    """

    if creditionals_json:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creditionals_json

    client = speech_v1p1beta1.SpeechClient()
    language_code = language_code
    sample_rate_hertz = sample_rate_hertz

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.MP3
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
        "enable_word_time_offsets": True,
    }
    audio = {"uri": storage_uri}

    # response = client.recognize(config, audio)
    # https://issue.life/questions/57559101
    # по ссылке как сделать индикатор
    operation = client.long_running_recognize(config, audio)
    response = operation.result()
    json_result = dict()
    json_result['words'] = list()

    for result in response.results:

        alternative = result.alternatives[0]

        for i, word in enumerate(alternative.words):
            json_result['words'].append({'id': i,
                                         'word': word.word,
                                         'start_time': word.start_time.seconds + word.start_time.nanos / 1000 ** 3,
                                         'end_time': word.end_time.seconds + word.end_time.nanos / 1000 ** 3
                                         })

    json_result['afterRecognize'] = True
    json_result = json.dumps(json_result)
    return json_result


def main(body):

    request = json.loads(body)

    mp3_url_storage = request['mp3_url_storage']
    language = request['language']
    logger.info(f"Audio for {request['video_uuid']} recognize")
    try:
        captions = recognize(mp3_url_storage, 'modules/config-google.json', language)
    except Exception as err:
        logger.error(err)
        raise err

    data = {
        'jwt_token': request['jwt'],
        'video_uuid': request['video_uuid'],
        'captions': captions,
        'status': 'Done'
    }
    requests.post(os.environ.get('WEBSITE_URL') + '/video/updata/', json=data)
    if 'DEBUG' in os.environ:
        websocket.sendSocket(request['jwt'], json.dumps({'status': 'Done', 'video_uuid': request['video_uuid']}))


if __name__ == '__main__':
    """
        При ошибки API. Перейти по ссылке - https://console.developers.google.com/apis/api/speech.googleapis.com/overview?project=263164491395
        Зарегать акк и включить Cloud Speech-to-Text API
    """


    async def callback(channel, body, envelope, properties):
        request = json.loads(body)
        data = {
            'jwt_token': request['jwt'],
            'video_uuid': request['video_uuid'],
            'status': 'Recognize'
        }
        requests.post(os.environ.get('WEBSITE_URL') + '/video/updata/', json=data)

        if 'DEBUG' in os.environ:
            websocket.sendSocket(request['jwt'], json.dumps({'status': 'Recognize', 'video_uuid': request['video_uuid']}))

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
        queue = os.environ.get('QUEUE_RECOGNIZE')

        if 'DEBUG' in os.environ:
            await channel.queue_declare(queue, durable=True)
        else:
            await channel.queue_declare(queue)
        await channel.basic_qos(prefetch_count=4, prefetch_size=0, connection_global=False)
        await channel.basic_consume(callback, queue)


    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(worker()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
