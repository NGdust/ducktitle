#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import json
import jwt
from datetime import datetime
import requests
import websockets
from modules.filebase import *
from modules.amqp import loop, send
from modules.probe import getProbe
from modules.downloader import Downloader
from modules.flask_validator.validator_engine import ValidatorEngine
from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger, swag_from
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from settings import ConfigProd, ConfigDev, configSwagger

from modules.logger import *
from modules.sentry_sdk import *


"""
Настройки проекта
"""

app = Flask(__name__)
app.config.from_object(ConfigProd if 'DEBUG' in os.environ else ConfigDev)
CORS(app)
swagger = Swagger(app, config=configSwagger)
validator = ValidatorEngine()
validator.init_app(app)

"""
База данных
"""

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
db.create_all()
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
session = scoped_session(sessionmaker(bind=engine))

"""
Endpoints
"""


@app.route('/video/default/<int:user_id>', methods=['GET'])
def default_user_video(user_id):
    new_preset = Preset(user_id=user_id)
    db.session.add(new_preset)
    db.session.commit()

    default_video = Video(user_id=user_id, url='https://suptitle.s3.us-west-1.wasabisys.com/default/DefaultVideo.mp4',
                          language_code='ru-RU')
    default_video.uuid = 'start'
    default_video.image = 'https://suptitle.s3.us-west-1.wasabisys.com/default/DefaultVideo.jpg'
    default_video.gif = 'https://suptitle.s3.us-west-1.wasabisys.com/default/DefaultVideo.gif'
    default_video.ready = 'Edit'
    default_video.description = 'Default video'
    default_video.duration = '297.308000'
    default_video.resolution = '640,360'
    default_video.captions = """{"words":[{"word":"Всем привет Сегодня хотел поговорить с вами о том Зачем","end_time":5.6,"start_time":0.9},{"word":"программисту участвовать в проектах","end_time":9.2,"start_time":5.6},{"word":"для чего это нужно в первую очередь","end_time":12.2,"start_time":9.2},{"word":"это нужно но если вы хотите найти работу для","end_time":15.2,"start_time":12.2},{"word":"себя или вы хотите найти свой","end_time":18.5,"start_time":15.2},{"word":"проект какого-то программиста кто","end_time":22,"start_time":18.5},{"word":"захочет с вами работать и развивать Этот проект и","end_time":26.2,"start_time":22},{"word":"также вы можете создать свой","end_time":29.2,"start_time":26.2},{"word":"проект о танцовщице это может","end_time":32.2,"start_time":29.2},{"word":"быть источником дохода такие как донаты ну","end_time":36.2,"start_time":32.2},{"word":"и вообще если социальными сетями то","end_time":40.5,"start_time":36.2},{"word":"люди которые там","end_time":43.5,"start_time":40.5},{"word":"активничает они набирают подписную","end_time":46.8,"start_time":43.5},{"word":"базу они становятся популярными также","end_time":50.3,"start_time":46.8},{"word":"но они с этого иметь деньги с","end_time":53.4,"start_time":50.3},{"word":"доходы Также","end_time":56.7,"start_time":53.4},{"word":"можно провести параллель то что люди на Ютюбе","end_time":59.8,"start_time":56.7},{"word":"которые создают свои ролики они тоже ищут популярности и","end_time":63.6,"start_time":59.8},{"word":"ещё того что у них они будут как-то","end_time":66.7,"start_time":63.6},{"word":"на рекламе как-то будет","end_time":70,"start_time":66.7},{"word":"общаться с другими людьми и","end_time":73,"start_time":70},{"word":"получается этого какую-то выгоду вот","end_time":76.9,"start_time":73},{"word":"и всё также в программировании это open-source","end_time":80.6,"start_time":76.9},{"word":"дает вам возможность налаживать","end_time":84.3,"start_time":80.6},{"word":"контакт с программистами но не с помощью там видео","end_time":87.8,"start_time":84.3},{"word":"или каких-то постов с помощью непосредственно","end_time":91.3,"start_time":87.8},{"word":"в самовыражении себя как программиста и","end_time":94.8,"start_time":91.3},{"word":"становления себя как программиста","end_time":98.2,"start_time":94.8},{"word":"Вот это основные направления","end_time":101.7,"start_time":98.2},{"word":"для чего это В принципе может пригодиться Давайте","end_time":105,"start_time":101.7},{"word":"тебе расскажу как это в общем и целом сделать","end_time":108.2,"start_time":105},{"word":"Одно из самых популярных площадок","end_time":111.3,"start_time":108.2},{"word":"для программирования это гитхаб большая","end_time":114.4,"start_time":111.3},{"word":"социальная сеть там где люди выкладывают код","end_time":117.4,"start_time":114.4},{"word":"для того чтобы найти openssource проект","end_time":120.6,"start_time":117.4},{"word":"вам нужно пойти в тренды и","end_time":124.4,"start_time":120.6},{"word":"в трендах найти проект которая не очень то","end_time":129.4,"start_time":124.4},{"word":"есть не имеет высокую популярность Почему","end_time":132.7,"start_time":129.4},{"word":"Потому что те люди которые будут принимать ваши Pull request а","end_time":135.9,"start_time":132.7},{"word":"на их ограниченное","end_time":139.1,"start_time":135.9},{"word":"количество популярные проекты максимальное число","end_time":142.5,"start_time":139.1},{"word":"людей стремиться И поэтому это может заниматься","end_time":145.6,"start_time":142.5},{"word":"долгое время чтобы получить какую-то отдачу как","end_time":151,"start_time":145.6},{"word":"вообще начать когда вы нашли вот этот проект то","end_time":155.3,"start_time":151},{"word":"вы можете во-первых","end_time":159.1,"start_time":155.3},{"word":"его установить у себя посмотреть","end_time":163.6,"start_time":159.1},{"word":"на ищу которые там есть то есть какие проблемы сейчас есть","end_time":166.8,"start_time":163.6},{"word":"в этом проекте и на","end_time":171,"start_time":166.8},{"word":"основании этого ещё что-то пофиксить","end_time":174.4,"start_time":171},{"word":"или добавить какую-то новую фичу тем","end_time":178.8,"start_time":174.4},{"word":"самым создав потом по реквесты получить","end_time":181.8,"start_time":178.8},{"word":"фидбек также рекомендую когда занимаешься","end_time":185,"start_time":181.8},{"word":"этим максимально полно описывать не","end_time":189.1,"start_time":185},{"word":"сухой текст списывать Что вы сделали чтобы в","end_time":192.1,"start_time":189.1},{"word":"Ну и для чего вообще это отправляется","end_time":195.6,"start_time":192.1},{"word":"тем самым вы сможете набрать","end_time":199,"start_time":195.6},{"word":"для себя контакты","end_time":202.3,"start_time":199},{"word":"этих программистов и возможно иметь","end_time":205.6,"start_time":202.3},{"word":"какие-то отношения Потом иметь какие-то совместные проекты","end_time":208.8,"start_time":205.6},{"word":"возможно вас пригласят на работу самое","end_time":213.3,"start_time":208.8},{"word":"главное туда попасть чтобы вы пообщались","end_time":216.4,"start_time":213.3},{"word":"на одной волне и это","end_time":220.6,"start_time":216.4},{"word":"даст вам развитие во-первых как программиста вы","end_time":224.1,"start_time":220.6},{"word":"будете работать с реальным проектом смотреть","end_time":227.2,"start_time":224.1},{"word":"как люди пишут код и его читать и писать","end_time":230.2,"start_time":227.2},{"word":"самостоятельно также это","end_time":234,"start_time":230.2},{"word":"даст вам новые связи которые","end_time":237.6,"start_time":234},{"word":"вы можете потом на основании","end_time":240.6,"start_time":237.6},{"word":"этих связей получить работу либо сделать","end_time":243.7,"start_time":240.6},{"word":"какой-то совместный проект либо Вас","end_time":246.9,"start_time":243.7},{"word":"могут взять на уже на какие-то","end_time":249.9,"start_time":246.9},{"word":"деньги для того чтобы развивать Этот проект но всё","end_time":253.3,"start_time":249.9},{"word":"всегда начинается с Таких","end_time":257.2,"start_time":253.3},{"word":"вот социальных отношений в интернете поэтому","end_time":260.4,"start_time":257.2},{"word":"рекомендую не пренебрегайте этим шагом он позволит","end_time":263.4,"start_time":260.4},{"word":"вам быстрее расти как программист и","end_time":267.2,"start_time":263.4},{"word":"в резюме вы потом Можете свободно указывать","end_time":270.7,"start_time":267.2},{"word":"что вы участвовали в проекте","end_time":274.7,"start_time":270.7},{"word":"как Open Source проекты как разработчик","end_time":277.7,"start_time":274.7},{"word":"это всегда плюс ваши резюме","end_time":280.8,"start_time":277.7},{"word":"и многие работодатели Интересно","end_time":284.7,"start_time":280.8},{"word":"что люди участвуют в таких проектах Nippon","end_time":288.3,"start_time":284.7},{"word":"Source проектов Спасибо что смотрели Подписывайтесь","end_time":291.6,"start_time":288.3},{"word":"комментарии Всем пока","end_time":297.3,"start_time":291.6}]}"""
    default_video.id_preset = new_preset.id
    default_video.status = "Done"
    db.session.add(default_video)
    db.session.commit()
    return json.dumps({"status": "File add"}), 200


@app.route('/video/get_resolution/', methods=['POST'])
@validator('json', {
    'url': ['type:str']
})
def getResolution():
    url = request.json['url']
    try:
        resolutions = Downloader(url, None).getAvailableResolutions()
    except Exception as err:
        err = str(err)
        logger.error(err)
        return json.dumps({"error": err}), 404

    if not resolutions:
        return json.dumps({"error": "Not resolution"}), 200
    return json.dumps({"resolutions": resolutions}), 200


@app.route('/video/upload/file', methods=['POST'])
@swag_from('swagger/upload_file.yml')
@validator('form_data', {
    'jwt_token': ['required', 'type:str'],
    'language': ['required', 'type:str'],
    'default_language': ['required', 'type:str']
})
@validator('form_data_file', {
    'filename': 'file'
})
def upload_file():
    try:
        file = request.files['file']
        jwt_token = request.form.get('jwt_token')
        language = request.form.get('language')
        default_language = bool(request.form.get('default_language'))
    except KeyError as err:
        logger.error(str(err) + 'not find field')
        return json.dumps({'error': str(err) + 'not find field'}), 403

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    logger.info(f"Upload video file: {jwt_data['email']}")
    file.save(file_path)

    updateDefaultLanguage(default_language, jwt_token, language)

    # Проверка, подходит ли видео под наши параметры
    fileParametrs = getProbe(file_path)
    err = fileParametrs.checkError(app.config['ALLOWED_EXTENSIONS'])
    if err:
        # Если выдает ошибку удаляем временный файл и отправляем обратно текст ошибки
        os.remove(file_path)
        logger.error(err)
        return json.dumps({"status": err}), 200

    # Получаем метаданные о видео
    duration, resolution = fileParametrs.getParam()

    # Загрузка в Storage
    transport = WassabiStorageTransport(user_email=jwt_data['email'], from_filename=file_path)
    try:
        url_video_in_storage = transport.upload()
        logger.info(url_video_in_storage)
    except Exception as err:
        os.remove(file_path)
        logger.error(err)
        return json.dumps({"error": err}), 200

    # Создание видео в БД
    new_preset = Preset(user_id=jwt_data['user_id'])
    db.session.add(new_preset)
    db.session.commit()

    new_video = Video(user_id=jwt_data['user_id'], url=url_video_in_storage, language_code=language)
    new_video.id_preset = new_preset.id
    new_video.duration = duration
    new_video.resolution = resolution
    new_video.description = str(datetime.today().strftime("%d-%m-%Y %H:%M"))
    db.session.add(new_video)
    db.session.commit()

    # Отправка в очередь. Выдираем аудио и конвертим текст
    body = {
        'jwt': jwt_token,
        'video_uuid': new_video.uuid,
        'duration': new_video.duration,
        'url': url_video_in_storage,
        'language': language
    }

    # Удаление временного файла
    os.remove(file_path)

    loop.run_until_complete(send(body, os.environ.get('QUEUE_EXTRACTOR')))
    requests.post(app.config['HOST_AUTH'] + '/api/v1/update_limit_user/', json={"jwt_token": jwt_token, "count": 1})
    logger.info(f"Video {new_video.uuid} send to extract")
    return json.dumps({"status": "loaded", "video_uuid": new_video.uuid}), 200


@app.route('/video/upload/url', methods=['POST'])
@swag_from('swagger/upload_url.yml')
@validator('json', {
    'url': ['type:str'],
    'jwt_token': ['required', 'type:str'],
    'language': ['required', 'type:str'],
    'default_language': ['required', 'type:str'],
    'resolution': ['type:str'],
    'best_resolution': ['type:bool']
})
def upload_url():
    try:
        url = request.json['url']
        jwt_token = request.json['jwt_token']
        language = request.json['language']
        default_language = request.json['default_language']
    except KeyError as err:
        logger.error(str(err) + 'not find field')
        return json.dumps({'error': str(err) + 'not find field'}), 404

    try:
        Downloader(url, None)
    except Exception as err:
        err = str(err)
        logger.error(err)
        return json.dumps({"error": err}), 404

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 404

    updateDefaultLanguage(default_language, jwt_token, language)

    # Создание видео в БД
    new_preset = Preset(user_id=jwt_data['user_id'])
    db.session.add(new_preset)
    db.session.commit()

    new_video = Video(user_id=jwt_data['user_id'], url='', language_code=language)
    new_video.id_preset = new_preset.id
    new_video.description = str(datetime.today().strftime("%d-%m-%Y %H:%M"))
    db.session.add(new_video)
    db.session.commit()

    # Отправка в очередь. Скачивание видео.
    body = {
        'jwt': jwt_token,
        'video_uuid': new_video.uuid,
        'url': url,
        'language': language
    }
    try: body['resolution'] = request.json['resolution']
    except: pass
    try: body['best_resolution'] = request.json['best_resolution']
    except: pass

    loop.run_until_complete(send(body, os.environ.get('QUEUE_DOWNLOAD_VIDEO')))
    requests.post(app.config['HOST_AUTH'] + '/api/v1/update_limit_user/', json={"jwt_token": jwt_token, "count": 1})
    logger.info(f"Video url {url} send to service_download_video")
    return json.dumps({"status": "loaded", "video_uuid": new_video.uuid}), 200


@app.route('/video/delete/', methods=['POST'])
@swag_from('swagger/delete.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def delete_video():
    video_uuid = request.json['video_uuid']
    try:
        jwt_token = request.json['jwt_token']
    except KeyError as err:
        logger.error(str(err) + 'not find field')
        return json.dumps({'error': str(err) + 'not find field'}), 403

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).first()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    preset = db.session.query(Preset).filter_by(id=video.id_preset).first()
    db.session.delete(video)
    db.session.delete(preset)
    db.session.commit()
    logger.info(f"Video {video.uuid} deleted")
    return json.dumps({"status": "File delete"}), 200


@app.route('/video/create/', methods=['POST'])
@swag_from('swagger/create.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'language': ['required', 'type:str'],
    'duration': ['required', 'type:float'],
    'resolution': ['required', 'type:str'],
    'url_video_in_storage': ['required', 'type:str']
})
def create_video():
    try:
        jwt_token = request.json['jwt_token']
        language = request.json['language']
        duration = request.json['duration']
        resolution = request.json['resolution']
        url_video_in_storage = request.json['url_video_in_storage']
    except KeyError as err:
        logger.error(str(err) + 'not find field')
        return json.dumps({'error': str(err) + 'not find field'}), 403

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    new_preset = Preset(user_id=jwt_data['user_id'])
    db.session.add(new_preset)
    db.session.commit()

    new_video = Video(user_id=jwt_data['user_id'], url=url_video_in_storage, language_code=language)
    new_video.id_preset = new_preset.id
    new_video.duration = duration
    new_video.resolution = resolution
    new_video.description = str(datetime.today().strftime("%d-%m-%Y %H:%M"))
    db.session.add(new_video)
    db.session.commit()

    logger.info(f"Video {new_video.uuid} create")
    # send_socket(jwt_token, json.dumps({"status": "Video updated"}))
    return json.dumps({"status": "Video create",
                       'video_uuid': new_video.uuid,
                       'video_url': new_video.url,
                       'language': new_video.language_code}), 200


@app.route('/video/updata/', methods=['POST'])
@swag_from('swagger/updata.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def update_video():
    try:
        jwt_token = request.json.pop('jwt_token')
        video_uuid = request.json.pop('video_uuid')
    except KeyError as err:
        logger.error(str(err) + 'not find field')
        return json.dumps({'error': str(err) + 'not find field'}), 403

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": str(err)}), 403

    try:
        db.session.query(Video).filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).update(request.json)
        db.session.commit()
    except ProgrammingError as err:
        logger.error(err)
        return json.dumps({"error": str(err)}), 403
    except InvalidRequestError as err:
        try:
            var = re.match('.*?has no property \'(.*?)\'', str(err)).group(1)
            err = f'Unknown field {var}'
            logger.error(err)
            return json.dumps({"error": err}), 403
        except:
            logger.error(err)
            return json.dumps({"error": str(err)}), 403

    logger.info(f"Video {video_uuid} updated")
    return json.dumps({"status": "Video updated"}), 200


@app.route('/video/add_caption/', methods=['POST'])
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str'],
    'id_captions': ['required', 'type:int']
})
def add_caption():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']
    id_captions = request.json['id_captions']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    captions = json.loads(video.captions)
    lastId = captions.sort(key=captions['id'], reverse=True)[-1]

    try:
        newStartTime = captions[id_captions-1]['start']
        newEndTime = captions[id_captions+1]['end']
        newCaptions = captions[0:id_captions] + [{'id': lastId,
                                                  'start': newStartTime,
                                                  'end': newEndTime,
                                                  'word': ""}] + captions[id_captions:]
    except:
        err = 'Could not add caption'
        logger.error(err)
        return json.dumps({"error": err}), 200

    video.captions = newCaptions
    db.session.commit()

    logger.info(f"Video {video_uuid}: update element caption")
    return json.dumps({"status": "Element update"}), 200


@app.route('/video/delete_caption/', methods=['POST'])
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str'],
    'id_captions': ['required', 'type:int']
})
def delete_caption():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']
    id_captions = request.json['id_captions']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    captions = json.loads(video.captions)

    try:
        del captions[id_captions]
    except:
        err = 'Could not delete caption'
        logger.error(err)
        return json.dumps({"error": err}), 200

    video.captions = json.dumps(captions)
    db.session.commit()
    logger.info(f"Video {video_uuid}: delete element caption")
    return json.dumps({"status": "Delete caption"}), 200


@app.route('/video/get_status_video/', methods=['POST'])
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def get_status_video():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    return json.dumps({"status": video.status}), 200


@app.route('/video/edit_video/', methods=['POST'])
@swag_from('swagger/edit_video.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def edit_video():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    if len(json.loads(video.captions)['words']) <= 0:
        logger.info(f"Not words in captions")
        return json.dumps({"status": 'Not words in captions'}), 200

    video.ready = 'Download'
    db.session.commit()

    preset = Preset.query.filter_by(id=video.id_preset).one()
    # Отправка в очередь. Выдираем аудио и конвертим текст
    preset.textSize = preset.realTextSize
    body = {
        'jwt_token': jwt_token,
        'video_uuid': video.uuid,
        'url_video': video.url,
        'duration': video.duration,
        'resolution': video.resolution,
        'preset': str(preset),
        'captions': video.captions,
    }
    loop.run_until_complete(send(body, os.environ.get('QUEUE_EDITOR')))
    print(" [x] Sent video to editor")
    logger.info(f"Video {video.uuid} sent video to editor")
    return json.dumps({"status": 'Edition'}), 200


@app.route('/video/get_list_drafts_video/', methods=['POST'])
@swag_from('swagger/get_list_video.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'limit': ['required', 'type:int'],
    'offset': ['required', 'type:int']
})
def get_list_drafts_video():
    jwt_token = request.json['jwt_token']
    limit = request.json['limit']
    offset = request.json['offset']
    contents = []

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    for video in Video.query.filter_by(user_id=jwt_data['user_id'], ready='Edit').order_by(Video.id.desc())[
                 offset:offset + limit]:
        contents.append({
            'uuid': video.uuid,
            'ready': video.ready,
            'preview': video.image,
            'previewGif': video.gif,
            'videoName': video.url.split('/')[-1],
            'description': video.description,
        })
    return json.dumps({"video": contents}), 200


@app.route('/video/get_list_complete_video/', methods=['POST'])
@swag_from('swagger/get_list_video.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'limit': ['required', 'type:int'],
    'offset': ['required', 'type:int']
})
def get_list_complete_video():
    jwt_token = request.json['jwt_token']
    limit = request.json['limit']
    offset = request.json['offset']
    contents = []

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    for video in Video.query.filter_by(user_id=jwt_data['user_id'], ready='Download').order_by(Video.id.desc())[
                 offset:offset + limit]:
        contents.append({
            'uuid': video.uuid,
            'ready': video.ready,
            'preview': video.image,
            'previewGif': video.gif,
            'videoName': video.url.split('/')[-1],
            'description': video.description,
        })
    return json.dumps({"video": contents}), 200


@app.route('/video/get_single_video/', methods=['POST'])
@swag_from('swagger/get_single_video.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def get_single_video():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    contents = {
        'uuid': video.uuid,
        'user_id': video.user_id,
        'id_preset': video.id_preset,
        'description': video.description,
        'url': video.url,
        'ready': video.ready,
        'status': video.status,
        'preview': video.image,
        'videoName': video.url.split('/')[-1],
        'duration': video.duration,
        'resolution': video.resolution,
        'captions': video.captions,
        'result_url': video.result_url,
        'result_srt': video.result_srt,
    }
    return json.dumps({"video": contents}), 200


@app.route('/video/get_srt/', methods=['POST'])
@swag_from('swagger/get_srt.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def get_srt():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    filename = video.url.split('/')[-1].split('.')[0]
    file_srt = app.config['UPLOAD_FOLDER'] + f'/{filename}.srt'

    print(' [x] Generate SRT')
    i = 1
    srt = ''
    captions = json.loads(video.captions)
    for word in captions['words']:
        start_time = datetime.strftime(datetime.utcfromtimestamp(float(word['start_time'])), "%H:%M:%S,%f")[0:-3]
        end_time = datetime.strftime(datetime.utcfromtimestamp(float(word['end_time'])), "%H:%M:%S,%f")[0:-3]
        srt += f"""{i}\n{start_time} --> {end_time}\n{word['word']}\n"""
        i += 1

    with open(file_srt, 'a') as file:
        file.write(srt)

    # Загрузка в Storage
    transport = WassabiStorageTransport(user_email=jwt_data['email'], from_filename=file_srt)
    try:
        srt_storage = transport.upload()
        logger.info(srt_storage)
    except Exception as err:
        os.remove(file_srt)
        logger.error(err)
        return json.dumps({"error": err}), 200

    os.remove(file_srt)
    return json.dumps({"srt_url": srt_storage}), 200


@app.route('/video/get_transcript/', methods=['POST'])
@swag_from('swagger/get_transcript.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def get_transcript():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    filename = video.url.split('/')[-1].split('.')[0]
    file_txt = app.config['UPLOAD_FOLDER'] + f'/{filename}.txt'

    print(' [x] Generate transcript')
    captions = json.loads(video.captions)
    text = ''
    for word in captions['words']:
        text += f"""{word['word']} """

    with open(file_txt, 'a') as file:
        file.write(text)

    # Загрузка в Storage
    transport = WassabiStorageTransport(user_email=jwt_data['email'], from_filename=file_txt)
    try:
        txt_storage = transport.upload()
        logger.info(txt_storage)
    except Exception as err:
        os.remove(file_txt)
        logger.error(err)
        return json.dumps({"error": err}), 200

    os.remove(file_txt)
    return json.dumps({"text": text, "txt_url": txt_storage}), 200


@app.route('/video/change_ready_video/', methods=['POST'])
@swag_from('swagger/change_ready_video.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str'],
    'status': ['required', 'type:str']
})
def change_ready_video():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    video.ready = request.json['status']
    db.session.commit()
    logger.info(f"Video {video.uuid} change ready to '{video.ready}'")
    return json.dumps({"status": 'ok'}), 200


@app.route('/video/preset_update/', methods=['POST'])
@swag_from('swagger/preset_update.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def preset_update():
    jwt_token = request.json.pop('jwt_token')
    video_uuid = request.json.pop('video_uuid')

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).first()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    try:
        Preset.query.filter_by(id=video.id_preset).first()
    except:
        err = f'Video was not found with uuid: {video_uuid}. id_preset null'
        logger.error(err)
        return json.dumps({"error": err}), 200

    try:
        db.session.query(Preset).filter_by(id=video.id_preset).update(request.json)
        db.session.commit()
    except ProgrammingError as err:
        logger.error(err)
        return json.dumps({"error": str(err)}), 200
    except InvalidRequestError as err:
        try:
            logger.error(err)
            var = re.match('.*?has no property \'(.*?)\'', str(err)).group(1)
            return json.dumps({"error": f'Unknown field {var}'}), 200
        except:
            return json.dumps({"error": str(err)}), 200

    logger.info(f"Video {video.uuid} preset update -- id-{video.id_preset}")
    return json.dumps({"status": "Preset updated"}), 200

@app.route('/video/get_preset/', methods=['POST'])
@swag_from('swagger/get_preset.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'video_uuid': ['required', 'type:str']
})
def get_preset():
    jwt_token = request.json['jwt_token']
    video_uuid = request.json['video_uuid']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        video = Video.query.filter_by(uuid=video_uuid, user_id=jwt_data['user_id']).one()
    except:
        err = f'Video was not found with uuid: {video_uuid}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    presets = db.session.query(Preset).filter_by(id=video.id_preset).first()
    if presets == None:
        return json.dumps({"presetError": 'Not exist'}), 200
    body = {
        'fontColor': presets.fontColor,
        'backgroundColor': presets.backgroundColor,
        'fontOpacity': presets.fontOpacity,
        'backgroundOpacity': presets.backgroundOpacity,
        'font': presets.font,
        'textSize': presets.textSize,
        'bold': presets.bold,
        'italic': presets.italic,
        'fullLengthBackground': presets.fullLengthBackground,
        'backgroundShapeSquare': presets.backgroundShapeSquare,
        'verticalAlign': presets.verticalAlign,
        'horizontalAlign': presets.horizontalAlign,
        'aspectRatio': presets.aspectRatio,
        'progressBar': presets.progressBar,
    }

    return json.dumps({"preset": body}), 200


@app.route('/video/append_collection/', methods=['POST'])
@swag_from('swagger/append_collection.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'id_preset': ['required', 'type:int']
})
def append_collection():
    jwt_token = request.json['jwt_token']
    id_preset = request.json['id_preset']

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    try:
        preset = Preset.query.filter_by(id=id_preset, user_id=jwt_data['user_id']).one()
    except:
        err = f'Preset was not found with id: {id_preset}'
        logger.error(err)
        return json.dumps({"error": err}), 200

    append_collection = Collection(user_id=jwt_data['user_id'], preset_id=preset.id)
    db.session.add(append_collection)
    db.session.commit()

    return json.dumps({"status": "Appended"}), 200


@app.route('/video/get_collection/', methods=['POST'])
@swag_from('swagger/get_collection.yml')
@validator('json', {
    'jwt_token': ['required', 'type:str'],
    'id_preset': ['required', 'type:int']
})
def get_collection():
    jwt_token = request.json.pop('jwt_token')

    try:
        collection = Collection.query.filter_by(user_id=jwt_data['user_id']).all()
    except:
        err = f'Collection was not found'
        logger.error(err)
        return json.dumps({"error": err}), 200

    try:
        jwt_data = jwt.decode(jwt_token, verify=False)
    except:
        err = "Bad jwt_token"
        logger.error(err)
        return json.dumps({'error': err}), 403

    data = []
    for item in collection:
        preset = Preset.query.filter_by(id=item.preset_id).one()
        data.append(preset)

    return json.dumps({"collection": data}), 200


async def send_socket(jwt, msg):
    import ssl
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    ssl_context.load_cert_chain(
        os.environ.get('WEBSOCKET_CRT'),
        os.environ.get('WEBSOCKET_KEY'))

    async with websockets.connect(os.environ.get('WEBSOCKET_HOST'), ssl=ssl_context) as ws:
        await ws.send(json.dumps({'jwt': jwt, 'msg': msg}))
        await ws.close()


def updateDefaultLanguage(default_language, jwt_token, language):
    if default_language:
        data = {
            'jwt_token': jwt_token,
            'default_language': language
        }
        response = requests.post(os.environ.get('WEBSITE_URL') + '/api/v1/change_default_language/', json=data)
        print(' [X] Change default language. Status code - ', response.status_code)


if __name__ == '__main__':
    port = 6001
    if 'DEBUG' in os.environ:
        port = os.environ.get('PORT')
    app.run(host=os.environ.get('IP'), port=port)
