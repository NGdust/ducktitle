import json
import os
import unittest

import requests
from app import app, db
from modules.probe import getProbe
from werkzeug.datastructures import FileStorage

class TestApi(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.testapp = app.test_client()
        self.youtube_video_uuid = None
        db.create_all()

        self.jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1IiwiZXhwIjoxNTk2MTg2NDc5LCJlbWFpbCI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1In0.h9EmyoD51sRPClR5qaDVlMzna7kNdTZ5A7oqcAwgNx0'

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_upload_video_file(self):
        my_file = FileStorage(
            stream=open(os.path.join("testFile/test.mp4"), "rb"),
            filename="test.mp4",
            content_type="video/mpeg",
        ),
        responce = self.testapp.post(f'/video/upload/file', data=dict(
                               file=my_file,
                               jwt_token=self.jwt_token,
                               language='en_EN',
                               default_language='en_EN',
                           ), follow_redirects=True)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('loaded' in json.loads(responce.data)['status'], True)
        self.assertEqual('video_uuid' in json.loads(responce.data), True)

    def test_get_resolution_youtube(self):
        data = {
            "url": "https://www.youtube.com/watch?v=ZnLkhOdSAz0"
        }
        responce = self.testapp.post(f'/video/get_resolution/', json=data)
        print(responce.data)
        self.assertEqual('resolutions' in json.loads(responce.data), True)
        self.assertEqual(len(json.loads(responce.data)['resolutions']) > 0, True)

    def test_get_resolution_instagram(self):
        data = {
            "url": "https://www.instagram.com/p/CHtAgciDAO4/"
        }
        responce = self.testapp.post(f'/video/get_resolution/', json=data)
        print(responce.data)
        self.assertEqual('error' in json.loads(responce.data), True)
        self.assertEqual(json.loads(responce.data)['error'], "Couldn\'t get resolutions")

    def test_get_resolution(self):
        data = {
            "url": "https://suptitle.s3.us-west-1.wasabisys.com/kvando.test@mail.ru/Adovye_novosti_iPhone_12_za_40_000_no_bez_vazhnoi_shtuczki_i_tainy_iOS_14-144p.mp4"
        }
        responce = self.testapp.post(f'/video/get_resolution/', json=data)
        print(responce.data)
        self.assertEqual('error' in json.loads(responce.data), True)
        self.assertEqual(json.loads(responce.data)['error'], "Couldn\'t get resolutions")

    def test_upload_video_url_youtube(self):
        data = {
            "url": "https://www.youtube.com/watch?v=ZnLkhOdSAz0",
            "jwt_token": self.jwt_token,
            "language": "ru",
            "default_language": "ru",
            "best_resolution": 0
        }
        responce = self.testapp.post(f'/video/upload/url', json=data)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('loaded' in json.loads(responce.data)['status'], True)
        self.assertEqual('video_uuid' in json.loads(responce.data), True)
        youtube_video_uuid = json.loads(responce.data)['video_uuid']

        data = {'jwt_token': self.jwt_token,
                'video_uuid': youtube_video_uuid}
        responce = self.testapp.post('/video/delete/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'File delete')


    def test_upload_video_url_instagram(self):
        data = {
            "language": "ru",
            "default_language": "ru",
            "jwt_token": self.jwt_token,
            "url": "https://www.instagram.com/p/CHtAgciDAO4/",
            "best_resolution": 0
        }
        responce = self.testapp.post(f'/video/upload/url', json=data)
        print(responce)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('loaded' in json.loads(responce.data)['status'], True)
        self.assertEqual('video_uuid' in json.loads(responce.data), True)
        youtube_video_uuid = json.loads(responce.data)['video_uuid']

        data = {'jwt_token': self.jwt_token,
                'video_uuid': youtube_video_uuid}
        responce = self.testapp.post('/video/delete/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'File delete')

    def test_upload_video_url(self):
        data = {
            "language": "ru",
            "default_language": "ru",
            "jwt_token": self.jwt_token,
            "url": "https://suptitle.s3.us-west-1.wasabisys.com/kvando.test@mail.ru/Adovye_novosti_iPhone_12_za_40_000_no_bez_vazhnoi_shtuczki_i_tainy_iOS_14-144p.mp4",
            "best_resolution": 0
        }
        responce = self.testapp.post(f'/video/upload/url', json=data)
        print(responce)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('loaded' in json.loads(responce.data)['status'], True)
        self.assertEqual('video_uuid' in json.loads(responce.data), True)
        youtube_video_uuid = json.loads(responce.data)['video_uuid']

        data = {'jwt_token': self.jwt_token,
                'video_uuid': youtube_video_uuid}
        responce = self.testapp.post('/video/delete/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'File delete')

    def test_a_default_video(self):
        responce = self.testapp.get(f'/video/default/{1}')
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('File add' in json.loads(responce.data)['status'], True)

    def test_get_status_video(self):
        data = {
            'jwt_token': self.jwt_token,
            'video_uuid': 'start'
        }
        responce = self.testapp.post(f'/video/get_status_video/', json=data)
        self.assertEqual('status' in json.loads(responce.data), True)


    def test_add_caption(self):
        pass

    def test_delete_caption(self):
        pass


    """ Тесты на получение данных """

    def test_get_list_complete_video(self):
        data = {'jwt_token': self.jwt_token,
                'limit': 50,
                'offset': 0}
        responce = self.testapp.post('/video/get_list_complete_video/', json=data)
        self.assertEqual(responce.status_code, 200)

    def test_get_list_drafts_video(self):
        data = {'jwt_token': self.jwt_token,
                'limit': 50,
                'offset': 0}
        responce = self.testapp.post('/video/get_list_drafts_video/', json=data)
        self.assertEqual(responce.status_code, 200)

    def test_get_single_video(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/get_single_video/', json=data)
        self.assertEqual('video' in json.loads(responce.data), True)

    def test_get_preset(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/get_preset/', json=data)
        print(json.loads(responce.data))
        self.assertEqual('preset' in json.loads(responce.data), True)

    def test_get_srt(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/get_srt/', json=data)
        self.assertEqual('srt_url' in json.loads(responce.data), True)
        urlSrt = json.loads(responce.data)['srt_url']
        responce = requests.get(urlSrt)
        self.assertEqual(responce.status_code, 200)

    def test_get_transcript(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/get_transcript/', json=data)
        self.assertEqual('txt_url' in json.loads(responce.data), True)
        urlSrt = json.loads(responce.data)['txt_url']
        responce = requests.get(urlSrt)
        self.assertEqual(responce.status_code, 200)

    """ Тесты на изменения """

    def test_edit_video(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/edit_video/', json=data)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('Edition' in json.loads(responce.data)['status'], True)

    def test_updata(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start',
                'result_url': 'https://test.ru'}
        responce = self.testapp.post('/video/updata/', json=data)
        self.assertEqual('status' in json.loads(responce.data), True)
        self.assertEqual('Video updated' in json.loads(responce.data)['status'], True)

    def test_change_ready_video(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start',
                'status': 'Download'}
        responce = self.testapp.post('/video/change_ready_video/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'ok')

    def test_preset_update(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start',
                'name': 'Test NAME'}
        responce = self.testapp.post('/video/preset_update/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'Preset updated')

    def test_z_delete_video(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': 'start'}
        responce = self.testapp.post('/video/delete/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'File delete')

    def test_z_create_video(self):
        data = {
            "language": "ru",
            "duration": 32.56,
            "resolution": "320,240",
            "jwt_token": self.jwt_token,
            "url_video_in_storage": "blablabla"
        }
        responce = self.testapp.post('/video/create/', json=data)
        self.assertEqual(json.loads(responce.data)['status'], 'Video create')
        self.assertEqual('video_uuid' in json.loads(responce.data), True)
        self.assertEqual('video_url' in json.loads(responce.data), True)
        self.assertEqual('language' in json.loads(responce.data), True)

class TestErrorApi(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.testapp = app.test_client()
        self.youtube_video_uuid = None
        db.create_all()

        self.jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1IiwiZXhwIjoxNTk2MTg2NDc5LCJlbWFpbCI6ImdhcmdhbjR1a3ZAeWFuZGV4LnJ1In0.h9EmyoD51sRPClR5qaDVlMzna7kNdTZ5A7oqcAwgNx0'

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        db.drop_all()

    def test_get_single_video(self):
        data = {'jwt_token': self.jwt_token,
                'video_uuid': '123124132'}
        responce = self.testapp.post('/video/get_single_video/', json=data)
        self.assertEqual('error' in json.loads(responce.data), True)


class TestProbeMedia(unittest.TestCase):
    def setUp(self):
        self.filePath = 'testFile/test.mp4'
        self.probe = getProbe(file=self.filePath)

    def test_getParam(self):
        duration, resolution = self.probe.getParam()
        self.assertEqual(duration, 34.575)
        self.assertEqual(resolution, '640,360')

    def test_check_error(self):
        ALLOWED_EXTENSIONS = ['mp4', 'mov', 'm4v', 'MP4', 'MOV', 'm4v']
        err = self.probe.checkError(ALLOWED_EXTENSIONS)
        self.assertFalse(err)

class TestDownloader(unittest.TestCase):
    def setUp(self):
        self.youtubeURL = 'https://www.youtube.com/watch?v=VIghI06MI0o'
        self.dir = os.getcwd()

if __name__ == '__main__':
    unittest.main()
