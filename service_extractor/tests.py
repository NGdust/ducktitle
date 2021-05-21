import time
import unittest
import aiounittest
import requests
from main import Extractor

jwt_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMiwidXNlcm5hbWUiOiJkaW1hYnJ5YW5za3VtQGdtYWlsLmNvbSIsImV4cCI6MTU5NjU0ODA3OSwiZW1haWwiOiJkaW1hYnJ5YW5za3VtQGdtYWlsLmNvbSJ9.K3iwYdKoaOhYA2XS048EHQPDG3oW3-FZpZ7cmsycD7c'
url = 'https://suptitle.s3.us-west-1.wasabisys.com/dimabryanskum@gmail.com/3fb81192220840ed.mp4'

class TestExtractor(aiounittest.AsyncTestCase):
    def setUp(self):
        self.video = Extractor(url, 20.0, jwt_token)

    async def test_extract_audio(self):
        mp3_url_storage = await self.video.extract_audio()
        self.assertEqual(mp3_url_storage, "gs://suptitle-kvando.appspot.com/dimabryanskum@gmail.com/3fb81192220840ed.mp3")

    async def test_extract_image(self):
        image_url_storage = await self.video.get_image()
        responce = requests.get(image_url_storage)
        self.assertEqual(responce.status_code, 200)

    async def test_extract_gif(self):
        gif_url_storage = await self.video.get_gif()
        responce = requests.get(gif_url_storage)
        self.assertEqual(responce.status_code, 200)


if __name__ == '__main__':
    unittest.main()