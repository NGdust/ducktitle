from time import sleep

import jwt
import json
import asyncio
import aioamqp
import requests
from modules.downloader import Downloader
from modules.wsSendler import WebSocket

from modules.logger import *
from modules.sentry_sdk import *

websocket = WebSocket()


def deleteVideo(website_url, jwt_token, video_uuid):
    try:
        u = website_url + '/video/updata/'
        logger.info(f'send {u}')
        data = {'jwt_token': jwt_token, 'video_uuid': video_uuid}
        requests.post(u, json=data)
    except:
        pass

async def main(body, channel):
    request = json.loads(body)
    jwt_token = request['jwt']
    video_uuid = request['video_uuid']
    url_video = request['url']
    language = request['language']
    dir_video = os.getcwd() + '/transient'
    jwt_data = jwt.decode(jwt_token, verify=False)

    try: resolution = request['resolution']
    except: resolution = None

    try: best_resolution = bool(request['best_resolution'])
    except:best_resolution = None

    if 'DEBUG' in os.environ:
        websocket.sendSocket(jwt_token, json.dumps({'status': 'Download', 'video_uuid': video_uuid}))

    website_url = os.environ.get('WEBSITE_URL')
    # Download video
    info = ('best' if best_resolution else 'lower') if best_resolution is not None else ('best' if resolution is None else resolution)
    logger.info(f"Download {info} video file ({jwt_data['email']}): {url_video}")
    try:
        video = Downloader(url=url_video, dir=dir_video, resolution=resolution, best_resolution=best_resolution)
        file_path = video.download()
    except Exception as err:
        logger.error(err)
        _err = f"Don't download video by link: {url_video}"
        logger.error(_err)
        deleteVideo(website_url, jwt_token, video_uuid)
        if 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps({'error': f'Download: {_err}'}))
        return

    # Upload in Storage
    logger.info(f"Upload {info} video file in FileStorage ({jwt_data['email']}): {file_path}")
    try:
        url_video_in_storage = video.uploadInFileStorage(user_email=jwt_data['email'], file_path=file_path)
    except Exception as err:
        logger.error(err)
        deleteVideo(website_url, jwt_token, video_uuid)
        if 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps({'error': f'Download: {err}'}))
        return

    # Delete temp file
    try: os.remove(file_path)
    except: logger.error(f'Error remove file: {file_path}')

    # Update video in DB
    data = {
        'jwt_token': jwt_token,
        'video_uuid': video_uuid,
        'language_code': language,
        'url': url_video_in_storage,
        'duration': video.getDuration(),
        'resolution': video.getResolution()
    }
    u = website_url + '/video/updata/'
    logger.info(f'send {u}')

    try:
        response = requests.post(u, json=data)

        if response.status_code == 200:
            logger.info(f'Video updata, uuid: {video_uuid}')

            # Отправка в очередь. Выдираем аудио и конвертим текст
            body = {
                'jwt': jwt_token,
                'video_uuid': video_uuid,
                'duration': video.getDuration(),
                'url': url_video_in_storage,
                'language': language
            }

            logger.info(f"Video {video_uuid} send to extract")
            queue = os.environ.get('QUEUE_EXTRACTOR')

            if 'DEBUG' in os.environ:
                await channel.queue_declare(queue, durable=True)
            else:
                await channel.queue_declare(queue)
            await channel.basic_publish(json.dumps(body), '', queue)
        else:
            deleteVideo(website_url, jwt_token, video_uuid)
            raise Exception('Video not create')
    except (requests.exceptions.ConnectionError, Exception) as err:
        logger.error(err)
        err = f"Don't create video by link: {url_video_in_storage}"
        logger.error(err)
        deleteVideo(website_url, jwt_token, video_uuid)
        if 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps({'error': f'Download: {err}'}))

if __name__ == '__main__':
    async def callback(channel, body, envelope, properties):
        asyncio.create_task(main(body, channel))
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
        queue = os.environ.get('QUEUE_DOWNLOAD_VIDEO')

        if 'DEBUG' in os.environ:
            await channel.queue_declare(queue, durable=True)
        else:
            await channel.queue_declare(queue)
        await channel.basic_qos(prefetch_count=4, prefetch_size=0, connection_global=False)
        await channel.basic_consume(callback, queue_name=queue)


    loop = asyncio.get_event_loop()
    tasks = [
        loop.create_task(worker()),
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.run_forever()
