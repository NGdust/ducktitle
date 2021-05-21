import os
import re
import time
import shutil
import urllib
import subprocess
import requests
from pytube import YouTube
from pytube.exceptions import *
from urllib.request import urlretrieve
from .probe import getProbe
from .filebase import WassabiStorageTransport
from .logger import *


class Video:
    MAX_MIN_LENGTH = 20
    ALLOWED_EXTENSIONS = ['mp4', 'mov', 'm4v', 'MP4', 'MOV', 'm4v']
    ALLOWED_MEDIA_TYPES = ['video/mp4', 'video/quicktime', 'video/x-m4v']

    def __init__(self, url, dir, verify=True):

        if verify:
            self.verifyVideoByUrl(url)

        self.url = url
        self.video = None
        self.dir = dir
        self.resolutions = None
        self.duration = None
        self.resolution = None

    def verifyVideoByUrl(self, url):
        pattern = f'https:.*\.({"|".join(self.ALLOWED_EXTENSIONS)}).*?'
        try:
            response = requests.get(url, stream=True)
            type = response.headers['Content-Type']
            logger.info(f'Verify video {url}. Content-Type: {type}')

            if type in self.ALLOWED_MEDIA_TYPES:
                return True

            if type in ['binary/octet-stream']:
                try:
                    re.match(pattern, url).groups()
                    return True
                except:
                    logger.info(f'Video {url} don\'t match the pattern {pattern}')

            raise Exception(f'Incorrect for video Content-Type: {type}')
        except Exception as err:
            logger.info(str(err))
            raise Exception('Wrong link')

    def getDuration(self):
        return self.duration

    def getResolution(self):
        return self.resolution

    def getAvailableResolutions(self, with_fps=False):
        raise Exception("Couldn't get resolutions")

    def download(self):
        filename_video = self.url.split('?')[0].rsplit('/', 1)[-1].replace(' ', '_')
        os.makedirs(self.dir, exist_ok=True)
        path_file_video = f'{self.dir}/{filename_video}'

        start_time = time.time()
        urlretrieve(self.url, path_file_video)
        logger.info(f"Download video {filename_video} on {(time.time() - start_time):.3} seconds")

        # Проверка, подходит ли видео под наши параметры
        fileParametrs = getProbe(path_file_video)
        fileParametrs.checkError(self.ALLOWED_EXTENSIONS)
        duration, resolution = fileParametrs.getParam()

        try:
            self.validation_length(duration)
        except Exception as err:
            try: os.remove(path_file_video)
            except: logger.error(f'Error remove file: {path_file_video}')
            raise

        self.duration, self.resolution = duration, resolution

        return path_file_video

    @staticmethod
    def uploadInFileStorage(user_email, file_path):
        transport = WassabiStorageTransport(user_email=user_email, from_filename=file_path)

        try:
            url_video_in_storage = transport.upload()
        except Exception as err:
            logger.error(err)
            raise Exception(err)

        return url_video_in_storage

    @staticmethod
    def transliterate(title):
        # Слоаврь с заменами
        slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
                  'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
                  'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
                  'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
                  'ю': 'u', 'я': 'ja', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E',
                  'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
                  'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
                  'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
                  'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
                  '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
                  ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
                  '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
                  'Є': 'e', '—': '', '|': '', '.': ''}

        # Циклически заменяем все буквы в строке
        for key in slovar:
            if key in title:
                title = title.replace(key, slovar[key])
        return title

    @staticmethod
    def validation_length(seconds):
        seconds = int(float(seconds))
        min = seconds // 60; min = min if min > 9 else f'0{min}'
        sec = seconds % 60;  sec = sec if sec > 9 else f'0{sec}'
        logger.info(f"Length video {min}:{sec}")

        if seconds > Video.MAX_MIN_LENGTH * 60:
            err = f'Video length more than {Video.MAX_MIN_LENGTH} minutes'
            logger.error(err)
            raise Exception(err)


class YouTubeVideo(Video):

    def __init__(self, url, dir, resolution=None, best_resolution=None):
        super().__init__(url, dir, verify=False)
        self.resolution = resolution
        self.best_resolution = best_resolution
        for i in range(5):
            try:
                self.video = YouTube(self.url)
                logger.info('found url')
                break
            except (LiveStreamError, KeyError) as err:
                logger.error(err)
                err = 'Video is a live stream'
                logger.error(err)
                raise Exception(err)
            except (PytubeError, Exception) as err:
                logger.error(err)
                self.video = None

        if not self.video:
            err = 'Not found url'
            logger.error(err)
            raise Exception(err)

        self.validation_length(self.video.length)

    def getDuration(self):
        return self.duration

    def getResolution(self):
        return self.resolution

    def getAvailableResolutions(self):
        if self.resolutions is None:
            try:
                yt = self.video
                streams = yt.streams.filter(file_extension='mp4').order_by('resolution').desc()
                self.resolutions = [v.resolution for v in streams]
                self.resolutions = [i for n, i in enumerate(self.resolutions) if i not in self.resolutions[:n]]
            except (PytubeError, Exception) as err:
                logger.error(err)
                raise

        if not self.resolutions:
            raise Exception("Couldn't get resolutions")

        return self.resolutions

    def _downloadVideo(self, filename, subtype):
        videos = self.video.streams.filter(file_extension='mp4', resolution=self.resolution).order_by('resolution')
        video = videos.desc().first() if self.best_resolution is None or self.best_resolution else videos.first()
        filename_res = filename + '-' + video.resolution
        filename_video = 'video-' + filename_res

        start_time = time.time()
        video.download(self.dir, filename=filename_video)
        logger.info(f"Download video {filename_video} on {(time.time() - start_time):.3} seconds")
        path_file_video = f'{self.dir}/{filename_video}.{subtype}'

        # Проверка, подходит ли видео под наши параметры
        fileParametrs = getProbe(path_file_video)
        fileParametrs.checkError(self.ALLOWED_EXTENSIONS)

        # Получаем метаданные о видео
        self.duration, self.resolution = fileParametrs.getParam()

        return filename_res, filename_video, path_file_video

    def _downloadAudio(self, filename, subtype):
        audio = self.video.streams.filter(only_audio=True, file_extension=subtype).desc().first()
        filename_audio = 'audio-' + filename

        start_time = time.time()
        audio.download(self.dir, filename=filename_audio)
        logger.info(f"Download audio {filename_audio} on {(time.time() - start_time):.3} seconds")

        return filename_audio

    def _joinVideoAndAudio(self, filename_res, filename_video, path_file_video, filename_audio, subtype):
        path_file_res = f'{self.dir}/{filename_res}.{subtype}'
        path_file_audio = f'{self.dir}/{filename_audio}.{subtype}'

        start_time = time.time()
        command = ['ffmpeg', '-i', path_file_video, '-i', path_file_audio,
                   '-map', '0:v', '-map', '1:a', '-c', 'copy', path_file_res]
        logger.info(f"Join audio and video {filename_res} on {(time.time() - start_time):.3} seconds")
        subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE).communicate()
        # ffmpeg = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        # out, err = ffmpeg.communicate()
        # if (err):
        #     err = err.decode()
        #     print(err)
        #     raise Exception(err)

        return path_file_res, path_file_video, path_file_audio

    def download(self):
        try:
            subtype = 'mp4'
            filename = self.transliterate(self.video.title.replace(' ', '_'))
            filename_res, filename_video, path_file_video = self._downloadVideo(filename, subtype)
            filename_audio = self._downloadAudio(filename, subtype)
            path_file_res, path_file_video, path_file_audio = self._joinVideoAndAudio(
                filename_res, filename_video, path_file_video,
                filename_audio,
                subtype
            )

            try: os.remove(path_file_audio)
            except: logger.error(f'Error remove file: {path_file_audio}')

            try: os.remove(path_file_video)
            except: logger.error(f'Error remove file: {path_file_video}')

            if not os.path.exists(path_file_res):
                raise Exception('Failed to download the file')

            return path_file_res
        except AttributeError:
            err = f'Video with resolution {self.resolution} not found'
            logger.error(err)
            raise Exception(err)
        except Exception as err:
            logger.error(err)
            raise


class InstagramVideo(Video):

    def __init__(self, url, dir):
        pattern = 'https?:\/\/www\.instagram\.com\/(p|tv)\/.*'

        try: re.match(pattern, url).groups()
        except:
            raise Exception('Wrong link. Corrects https://www.instagram.com/p/XXXXXXXXXX/, https://www.instagram.com/tv/XXXXXXXXXX/')

        videos = requests.get(f"{url}?__a=1")
        json = videos.json()['graphql']['shortcode_media']
        video_url = json['video_url']

        super().__init__(video_url, dir)
        duration = json['video_duration']

        self.validation_length(duration)

        self.duration = duration
        dimensions = json['dimensions']
        self.resolution = f'{dimensions["width"]},{dimensions["height"]}'
        title_without_unicode = (json['title'].encode('ascii', 'ignore')).decode("utf-8")
        self.title = re.sub('[ ]{2,}', '', title_without_unicode).replace(' ', '_')

    def getDuration(self):
        return self.duration

    def getResolution(self):
        return self.resolution

    def getAvailableResolutions(self):
        raise Exception("Couldn't get resolutions")

    def download(self):
        try:
            file_path = f"{self.dir}/{self.title}.mp4"
            logger.info(f'Download {self.url}')

            start_time = time.time()
            urllib.request.urlretrieve(self.url, file_path)
            logger.info(f"Download video {self.title} on {(time.time() - start_time):.3} seconds")

            return file_path
        except Exception as err:
            err = str(err)
            logger.error(err)
            raise Exception(err)


class Downloader:

    def __init__(self, url, dir, resolution=None, best_resolution=None):
        self.url = url
        self.dir = dir
        self.video = None

        url = url.split('?', 1)[0]
        try:
            if 'youtube' in url:
                self.video = YouTubeVideo(self.url, self.dir, resolution=resolution, best_resolution=best_resolution)
            elif 'instagram' in url:
                self.video = InstagramVideo(self.url, self.dir)
            else:
                raise Exception
        except:
            try:
                self.video = Video(self.url, self.dir)
            except Exception as err:
                err = str(err)
                logger.error(err)
                raise

    def getDuration(self):
        try: return self.video.getDuration()
        except: raise

    def getResolution(self):
        try: return self.video.getResolution()
        except: raise

    def getAvailableResolutions(self):
        try: return self.video.getAvailableResolutions()
        except: raise

    def download(self):
        try: return self.video.download()
        except: raise

    def uploadInFileStorage(self, user_email, file_path):
        try: return self.video.uploadInFileStorage(user_email, file_path)
        except: raise




if __name__ == '__main__':
    urls = [
        'https://www.youtube.com/watch?v=TiDZHgzpxTw',
        'https://www.youtube.com/watch?v=UnLXXacusXM',
        'https://www.youtube.com/watch?v=5QY2_S9d4c4',
        'https://www.instagram.com/p/CHtAgciDAO4/',
        'https://suptitle.s3.us-west-1.wasabisys.com/kvando.test@mail.ru/Adovye_novosti_iPhone_12_za_40_000_no_bez_vazhnoi_shtuczki_i_tainy_iOS_14-144p.mp4'
    ]
    dir = os.getcwd() + '/videos/video'
    shutil.rmtree(dir, ignore_errors=True)
    os.makedirs(dir, exist_ok=True)
    for u in urls:
        try:
            d = Downloader(u, dir, best_resolution=False)
            try:
                print(d.getAvailableResolutions())
            except Exception as err:
                print(str(err))

            file_path = d.download()
            # file_path = d.download(resolution='144p')
            print(file_path)
            print()
        except Exception as err:
            print(str(err))