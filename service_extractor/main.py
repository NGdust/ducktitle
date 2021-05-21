import asyncio
import subprocess
import aioamqp
import json
import jwt
import os
import requests
from ffmpeg import FFmpeg
from modules.filebase import *
from modules.wsSendler import WebSocket

from modules.logger import *
from modules.sentry_sdk import *

websocket = WebSocket()

class Extractor:
    def __init__(self, url, duration, jwt_token):
        self.url = url
        self.duration = duration
        self.jwt_data = jwt.decode(jwt_token, verify=False)
        self.filename = self.url.split('/')[-1].split('.')[0]
        self.mp3_filename = self.filename + '.mp3'
        self.gif_filename = self.filename + '.gif'
        self.jpg_filename = self.filename + '.jpg'
        self.dir = os.getcwd() + '/transient/'

    async def extract_audio(self):
        try:
            logger.info(f"Video {self.url} extract audio for {self.jwt_data['email']}")
            file_path = self.dir + self.mp3_filename
            cmd = f'ffmpeg -i {self.url} -q:a 0 -map a {file_path}'
            logger.debug(cmd)

            p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            out, err = p.communicate()
            if err:
                err = err.decode()
                logger.error(err)
                raise Exception(err)

            transportFirebase = FirebaseStorageTransport(credentials='modules/config-google.json',
                                                         user_email=self.jwt_data['email'],
                                                         to_filename=f'{self.mp3_filename}',
                                                         from_filename=file_path)
            url = transportFirebase.upload()
            os.remove(file_path)
            return url
        except Exception as err:
            err = str(err)
            logger.error(err)
            err = f'Failed get image for video: {self.url}'
            logger.error(err)
            raise Exception(err)

    async def get_image(self):
        try:
            logger.info(f"Video {self.url} get image for {self.jwt_data['email']}")
            c = str(float(self.duration)//2)
            file_path = self.dir + self.jpg_filename

            cmd = f'ffmpeg -i {self.url} -ss {c} -vframes 1 {file_path}'
            logger.debug(cmd)

            p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            out, err = p.communicate()
            if err:
                err = err.decode()
                logger.error(err)
                raise Exception(err)

            transport = WassabiStorageTransport(user_email=self.jwt_data['email'], from_filename=file_path)
            try:
                url = transport.upload()
            except:
                os.remove(file_path)
                raise
            os.remove(file_path)
            return url
        except Exception as err:
            err = str(err)
            logger.error(err)
            err = f'Failed get image for video: {self.url}'
            logger.error(err)
            raise Exception(err)

    async def get_gif(self):
        try:
            logger.info(f"Video {self.url} get gif for {self.jwt_data['email']}")
            file_path = self.dir + self.gif_filename

            if float(self.duration) <= 10.0:
                return None

            filter = '[0:v] fps=9,scale=480:-1,split [a][b];[a] palettegen=max_colors=128 ' \
                     '[p];[b][p] paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle'
            cmd = ['ffmpeg', '-ss', '3', '-t', '10', '-i', self.url, '-filter_complex', filter, file_path]
            cmd_log = ['ffmpeg', '-ss', '3', '-t', '10', '-i', self.url, '-filter_complex', f'\"{filter}\"', file_path]
            logger.debug(' '.join(cmd_log))

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            out, err = p.communicate()
            if err:
                err = err.decode()
                logger.error(err)
                raise Exception(err)

            transport = WassabiStorageTransport(user_email=self.jwt_data['email'], from_filename=file_path)
            try:
                url = transport.upload()
                logger.info(url)
            except Exception as err:
                os.remove(file_path)
                raise

            os.remove(file_path)
            return url
        except Exception as err:
            err = str(err)
            logger.error(err)
            err = f'Failed get gef for video: {self.url}'
            logger.error(err)
            raise Exception(err)


async def main(body, channel):
    jwt_token = None
    try:
        request = json.loads(body)
        jwt_token = request['jwt']

        if 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps({'status': 'Extract', 'video_uuid': request['video_uuid']}))

        video = Extractor(request['url'], request['duration'], jwt_token)
        gif_url_storage = await video.get_gif()
        image_url_storage = await video.get_image()
        mp3_url_storage = await video.extract_audio()

        if 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps(
                {'status': 'Extract', 'video_uuid': request['video_uuid'],
                 'image': image_url_storage, 'gif': gif_url_storage}))

        # Обновление картинки видео в БД
        data = {
            'jwt_token': request['jwt'],
            'video_uuid': request['video_uuid'],
            'image': image_url_storage,
            'gif': gif_url_storage,
            'status': 'Extract',
        }
        requests.post(os.environ.get('WEBSITE_URL') + '/video/updata/', json=data)

        # Отправка на распознавание текста
        body = {
            'jwt': jwt_token,
            'video_uuid': request['video_uuid'],
            'mp3_url_storage': mp3_url_storage,
            'language': request['language'],
        }
        logger.info(f"Video {request['video_uuid']} send to recognize")
        queue = os.environ.get('QUEUE_RECOGNIZE')

        if 'DEBUG' in os.environ:
            await channel.queue_declare(queue, durable=True)
        else:
            await channel.queue_declare(queue)
        await channel.basic_publish(json.dumps(body), '', queue)

    except Exception as err:
        err = str(err)
        logger.error(err)
        if jwt_token and 'DEBUG' in os.environ:
            websocket.sendSocket(jwt_token, json.dumps({'error': f'Extract: {err}'}))
        return


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
        queue = os.environ.get('QUEUE_EXTRACTOR')

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
