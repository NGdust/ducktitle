import time
import unittest
import requests
from main import recognize

url = 'gs://suptitle-kvando.appspot.com/dimabryanskum@gmail.com/3fb81192220840ed.mp3'

class TestRecognize(unittest.TestCase):

    def test_recognize_audio(self):
        data = recognize(url, 'modules/config-google.json')
        self.assertTrue('words' in data)


if __name__ == '__main__':
    unittest.main()