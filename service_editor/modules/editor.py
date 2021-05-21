import asyncio
import datetime
import json
import math
import os
import subprocess
import urllib
from ast import literal_eval as le
from urllib.request import urlretrieve
from PIL import ImageFont
import jwt
from .filebase import WassabiStorageTransport
from moviepy.editor import *
from modules.calculator import CalculatorParams
from modules.wsSendler import WebSocket

websocket = WebSocket()



class Editor:
    def __init__(self, urlVideo):
        self.urlVideo = urlVideo
        self.dirTransite = os.getcwd() + os.environ.get('UPLOAD_FOLDER') + '/'

        self.filename = self.urlVideo.split('/')[-1]
        self.outFilename = self.dirTransite + self.filename.split('.')[0] + '_result.' + self.filename.split('.')[1]
        self.cmdFile = self.dirTransite + self.filename.split('.')[0] + '.txt'



class DrawerVideo(Editor):
    def __init__(self, urlVideo, preset, captions, resolution, duration):
        super(DrawerVideo, self).__init__(urlVideo)
        self.dirFonts = os.getcwd() + '/fonts/'
        self.preset = json.loads(preset)
        self.captions = json.loads(captions)
        # self.header = header
        self.resolution = list(map(int, resolution.split(',')))
        self.duration = float(duration)
        self.aspectRatio = self.preset.pop("aspectRatio")
        self.progressBar = self.preset.pop("progressBar")

        self._getFontPath()

    # Берем нужный шрифт от параметров
    def _getFontPath(self):
        font = self.preset['font']
        isBold = self.preset.pop('bold')
        idItalic = self.preset.pop('italic')
        fontText = f'{self.dirFonts}{font}'
        fontUrl = f'https://index.kvando.tech/media/fonts/{font}/{font}.ttf'
        if isBold:
            fontUrl = f'https://index.kvando.tech/media/fonts/{font}/{font}_bold.ttf'
            fontText += '_bold'
        elif idItalic:
            fontUrl = f'https://index.kvando.tech/media/fonts/{font}/{font}_italic.ttf'
            fontText += '_italic'
        fontText += '.ttf'
        urllib.request.urlretrieve(fontUrl, fontText)
        self.preset['font'] = fontText

    def _drawBox(self, x_bg, y_bg, w, h, backgroundColor, backgroundOpasity, start, end):
        return f"drawbox=" \
               f"x={x_bg}:" \
               f"y={y_bg}:" \
               f"w={w}:" \
               f"h={h}:" \
               f"t=fill:" \
               f"color={backgroundColor}@{backgroundOpasity}:" \
               f"enable=between'(t,{start},{end})', "

    def _drawText(self, x_sub, y_sub, font, text, fontColor, fontOpasity, textSize, start, end):
        return f"drawtext=" \
               f"x={x_sub}:" \
               f"y={y_sub}:" \
               f"fontfile={font}:" \
               f"text='{text}':" \
               f"fontcolor={fontColor}@{fontOpasity}:" \
               f"fontsize={textSize}:" \
               f"enable=between'(t,{start},{end})', "


    def drawSubtitle(self):
        command = ''
        with open(self.cmdFile, 'a') as file:
            for word in self.captions['words']:
                if float(word['start_time']) < float(word['end_time']):
                    sub_params, out_bg_params = CalculatorParams(text=word['word'].replace("'", "`"),
                                                                 resolution=self.resolution, **self.preset).getParametrs()
                    command += self._drawBox(**out_bg_params, start=word['start_time'], end=word['end_time'])
                    for i in range(0, len(sub_params)):
                        command += self._drawText(**sub_params[i], start=word['start_time'],
                                                  end=word['end_time'])
            # Удаляем запятую в конце списка команд
            command = command[:-2]
            file.write(command)

    def drawHeader(self, headerText):
        header, out_bg_params = CalculatorParams(text=headerText, resolution=self.resolution,
                                                 verticalAlign=self.resolution[1] - 30).getParametrs()
        command = ''
        with open(self.cmdFile, 'a') as file:
            for param in header:
                command += self._drawText(**param, start=0, end=self.duration)
            file.write(command)

    def drawProgressBar(self, colorBar='00ff10', colorBg='ffffff', bgOpasity=0.2, y=5, h=5):
        delta = self.resolution[0] / self.duration
        last_time = 0
        x = 0
        # Первой создаем подложку для прогресс бара
        command = f'drawbox=x=0:y={y}:w={self.resolution[0]}:h={h}:t=fill:color={colorBg}@{bgOpasity}, '
        with open(self.cmdFile, 'a') as file:
            # Итерируемся по секундам и рисуем прогресс по частям
            for t in range(0, int(self.duration) + 2):
                command += f"drawbox=x=0:y={y}:w={x}:h={h}:t=fill:color={colorBar}@1:enable=between'(t,{last_time},{t})', "
                last_time = t
                x += delta

            file.write(command)


    def addSticker(self):
        command = f" [0:v][1:v] overlay=10:10:enable='between(t,1,2)', "
        with open(self.cmdFile, 'a') as file:
            file.write(command)

    def changeAspectRatio(self):
        if self.aspectRatio == "0":
            return
        aspect = self.aspectRatio .split(':')
        new_b = self.resolution[0] * int(aspect[1]) / int(aspect[0])
        command = f'scale={self.resolution[0]}:{new_b}:force_original_aspect_ratio=decrease,pad={self.resolution[0]}:{new_b}:(ow-iw)/2:(oh-ih)/2, '
        with open(self.cmdFile, 'a') as file:
            file.write(command)
        self.resolution[1] = new_b


class BuilderVideo(Editor):
    def __init__(self, jwt_token, video_uuid, urlVideo, duration):
        super(BuilderVideo, self).__init__(urlVideo)
        self.jwt_token = jwt_token
        self.video_uuid = video_uuid
        self.duration = float(duration)


    def _getProgressProccessRendering(self, t):
        # В начале рендеринга иногда показывает отрицательное время
        try:
            dur = datetime.datetime.strptime(t.split('=')[1], "%H:%M:%S.%f")
            totalSecond = datetime.timedelta(hours=dur.hour, minutes=dur.minute, seconds=dur.second).total_seconds()
            return math.ceil(totalSecond * 100 / self.duration)
        except:
            return 0

    def _sendProgressProcess(self, line, lastProgress):
        if 'time' in str(line.rstrip()) and 'frame' in str(line.rstrip()):
            # Делим строку по атрибутам
            for item in line.rstrip().split(' '):
                # Ищем атрибут time
                if 'time' in item:
                    progress = self._getProgressProccessRendering(item)
                    if progress != lastProgress:
                        lastProgress = progress
                        if 'DEBUG' in os.environ:
                            websocket.sendSocket(self.jwt_token,
                                        json.dumps({'progress': progress, 'video_uuid': self.video_uuid}))
                        print('---------------> ', progress, '%')
        return lastProgress

    def _uploadInFirebase(self, file):
        jwt_data = jwt.decode(self.jwt_token, verify=False)

        transport = WassabiStorageTransport(user_email=jwt_data['email'], from_filename=file)
        try:
            url = transport.upload()
        except Exception as err:
            raise

        return url


    def build(self):
        self.cmd = f"ffmpeg " \
                   f"-i {self.urlVideo} " \
                   f"-filter_complex_script " \
                   f"{self.cmdFile} " \
                   f"{self.outFilename}"
        p = subprocess.Popen(self.cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             universal_newlines=True)

        print(' [x] Start edit video')

        lastProgress = 0
        for line in p.stdout:
            lastProgress = self._sendProgressProcess(line, lastProgress)

        self.videoResultInStorage = ''
        if 'DEBUG' in os.environ:
            try:
                self.videoResultInStorage = self._uploadInFirebase(self.outFilename)
            except Exception as err:
                print(f' [X] Error in generate command file for ffmpeg. {err}')
            os.remove(self.outFilename)
            os.remove(self.cmdFile)
            websocket.sendSocket(self.jwt_token,json.dumps({'result_url': self.videoResultInStorage,
                                                            'video_uuid': self.video_uuid}))

        print(' [X] Edit complete')
        return self.videoResultInStorage


if __name__ == '__main__':
    jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1IiwiZXhwIjoxNTkxMzQ0NDUyLCJlbWFpbCI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1In0.69GYplJ4SBfHV4eS480Y9Kcn4oS9_wD86Wmarse-ToY"

    url = 'https://suptitle.s3.us-west-1.wasabisys.com/tishkinyura32@gmail.com/igor.mp4'
    captions = """{"words":[{"word":"Всем привет Сегодня хотел поговорить с вами о том Зачем","end_time":5.6,"start_time":0.9},{"word":"программисту участвовать в проектах","end_time":9.2,"start_time":5.6},{"word":"для чего это нужно в первую очередь","end_time":12.2,"start_time":9.2},{"word":"это нужно но если вы хотите найти работу для","end_time":15.2,"start_time":12.2},{"word":"себя или вы хотите найти свой","end_time":18.5,"start_time":15.2},{"word":"проект какого-то программиста кто","end_time":22,"start_time":18.5},{"word":"захочет с вами работать и развивать Этот проект и","end_time":26.2,"start_time":22},{"word":"также вы можете создать свой","end_time":29.2,"start_time":26.2},{"word":"проект о танцовщице это может","end_time":32.2,"start_time":29.2},{"word":"быть источником дохода такие как донаты ну","end_time":36.2,"start_time":32.2},{"word":"и вообще если социальными сетями то","end_time":40.5,"start_time":36.2},{"word":"люди которые там","end_time":43.5,"start_time":40.5},{"word":"активничает они набирают подписную","end_time":46.8,"start_time":43.5},{"word":"базу они становятся популярными также","end_time":50.3,"start_time":46.8},{"word":"но они с этого иметь деньги с","end_time":53.4,"start_time":50.3},{"word":"доходы Также","end_time":56.7,"start_time":53.4},{"word":"можно провести параллель то что люди на Ютюбе","end_time":59.8,"start_time":56.7},{"word":"которые создают свои ролики они тоже ищут популярности и","end_time":63.6,"start_time":59.8},{"word":"ещё того что у них они будут как-то","end_time":66.7,"start_time":63.6},{"word":"на рекламе как-то будет","end_time":70,"start_time":66.7},{"word":"общаться с другими людьми и","end_time":73,"start_time":70},{"word":"получается этого какую-то выгоду вот","end_time":76.9,"start_time":73},{"word":"и всё также в программировании это open-source","end_time":80.6,"start_time":76.9},{"word":"дает вам возможность налаживать","end_time":84.3,"start_time":80.6},{"word":"контакт с программистами но не с помощью там видео","end_time":87.8,"start_time":84.3},{"word":"или каких-то постов с помощью непосредственно","end_time":91.3,"start_time":87.8},{"word":"в самовыражении себя как программиста и","end_time":94.8,"start_time":91.3},{"word":"становления себя как программиста","end_time":98.2,"start_time":94.8},{"word":"Вот это основные направления","end_time":101.7,"start_time":98.2},{"word":"для чего это В принципе может пригодиться Давайте","end_time":105,"start_time":101.7},{"word":"тебе расскажу как это в общем и целом сделать","end_time":108.2,"start_time":105},{"word":"Одно из самых популярных площадок","end_time":111.3,"start_time":108.2},{"word":"для программирования это гитхаб большая","end_time":114.4,"start_time":111.3},{"word":"социальная сеть там где люди выкладывают код","end_time":117.4,"start_time":114.4},{"word":"для того чтобы найти openssource проект","end_time":120.6,"start_time":117.4},{"word":"вам нужно пойти в тренды и","end_time":124.4,"start_time":120.6},{"word":"в трендах найти проект которая не очень то","end_time":129.4,"start_time":124.4},{"word":"есть не имеет высокую популярность Почему","end_time":132.7,"start_time":129.4},{"word":"Потому что те люди которые будут принимать ваши Pull request а","end_time":135.9,"start_time":132.7},{"word":"на их ограниченное","end_time":139.1,"start_time":135.9},{"word":"количество популярные проекты максимальное число","end_time":142.5,"start_time":139.1},{"word":"людей стремиться И поэтому это может заниматься","end_time":145.6,"start_time":142.5},{"word":"долгое время чтобы получить какую-то отдачу как","end_time":151,"start_time":145.6},{"word":"вообще начать когда вы нашли вот этот проект то","end_time":155.3,"start_time":151},{"word":"вы можете во-первых","end_time":159.1,"start_time":155.3},{"word":"его установить у себя посмотреть","end_time":163.6,"start_time":159.1},{"word":"на ищу которые там есть то есть какие проблемы сейчас есть","end_time":166.8,"start_time":163.6},{"word":"в этом проекте и на","end_time":171,"start_time":166.8},{"word":"основании этого ещё что-то пофиксить","end_time":174.4,"start_time":171},{"word":"или добавить какую-то новую фичу тем","end_time":178.8,"start_time":174.4},{"word":"самым создав потом по реквесты получить","end_time":181.8,"start_time":178.8},{"word":"фидбек также рекомендую когда занимаешься","end_time":185,"start_time":181.8},{"word":"этим максимально полно описывать не","end_time":189.1,"start_time":185},{"word":"сухой текст списывать Что вы сделали чтобы в","end_time":192.1,"start_time":189.1},{"word":"Ну и для чего вообще это отправляется","end_time":195.6,"start_time":192.1},{"word":"тем самым вы сможете набрать","end_time":199,"start_time":195.6},{"word":"для себя контакты","end_time":202.3,"start_time":199},{"word":"этих программистов и возможно иметь","end_time":205.6,"start_time":202.3},{"word":"какие-то отношения Потом иметь какие-то совместные проекты","end_time":208.8,"start_time":205.6},{"word":"возможно вас пригласят на работу самое","end_time":213.3,"start_time":208.8},{"word":"главное туда попасть чтобы вы пообщались","end_time":216.4,"start_time":213.3},{"word":"на одной волне и это","end_time":220.6,"start_time":216.4},{"word":"даст вам развитие во-первых как программиста вы","end_time":224.1,"start_time":220.6},{"word":"будете работать с реальным проектом смотреть","end_time":227.2,"start_time":224.1},{"word":"как люди пишут код и его читать и писать","end_time":230.2,"start_time":227.2},{"word":"самостоятельно также это","end_time":234,"start_time":230.2},{"word":"даст вам новые связи которые","end_time":237.6,"start_time":234},{"word":"вы можете потом на основании","end_time":240.6,"start_time":237.6},{"word":"этих связей получить работу либо сделать","end_time":243.7,"start_time":240.6},{"word":"какой-то совместный проект либо Вас","end_time":246.9,"start_time":243.7},{"word":"могут взять на уже на какие-то","end_time":249.9,"start_time":246.9},{"word":"деньги для того чтобы развивать Этот проект но всё","end_time":253.3,"start_time":249.9},{"word":"всегда начинается с Таких","end_time":257.2,"start_time":253.3},{"word":"вот социальных отношений в интернете поэтому","end_time":260.4,"start_time":257.2},{"word":"рекомендую не пренебрегайте этим шагом он позволит","end_time":263.4,"start_time":260.4},{"word":"вам быстрее расти как программист и","end_time":267.2,"start_time":263.4},{"word":"в резюме вы потом Можете свободно указывать","end_time":270.7,"start_time":267.2},{"word":"что вы участвовали в проекте","end_time":274.7,"start_time":270.7},{"word":"как Open Source проекты как разработчик","end_time":277.7,"start_time":274.7},{"word":"это всегда плюс ваши резюме","end_time":280.8,"start_time":277.7},{"word":"и многие работодатели Интересно","end_time":284.7,"start_time":280.8},{"word":"что люди участвуют в таких проектах Nippon","end_time":288.3,"start_time":284.7},{"word":"Source проектов Спасибо что смотрели Подписывайтесь","end_time":291.6,"start_time":288.3},{"word":"комментарии Всем пока","end_time":297.3,"start_time":291.6}]}"""
    header = ''
    preset = ''
    resolution = '640,360'
    duration = '297.308000'
    dir = os.getcwd()

    preset = """{
        "font": "Arial",
        "textSize": 24,
        "backgroundOpacity": 0.5,
        "fontOpacity": 1,
        "fontColor": "ffffff",
        "backgroundColor": "000000",
        "verticalAlign": 13,
        "horizontalAlign": "center",
        "fullLengthBackground": true,
        "backgroundShapeSquare": true,
        "bold": false,
        "italic": false,
        "aspectRatio": "",
        "progressBar": true
    }"""

    drawer = DrawerVideo(url, preset, captions, resolution, duration)
    drawer.drawSubtitle()
    editor = BuilderVideo(jwt_token, "sdhgd", url, duration)
    editor.build()
