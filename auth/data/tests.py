import json

import jwt
from django.conf import settings
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_jwt.serializers import User
from rest_framework_jwt.utils import jwt_payload_handler


client = Client()

class ApiAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com', password='test')
        payload = jwt_payload_handler(self.user)
        self.jwt = jwt.encode(payload, settings.SECRET_KEY)
        client.get(reverse('pars_language'))

    def test_get_language(self):
        data = {'jwt_token': self.jwt.decode()}
        responce = client.post(
            reverse('get_language'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertTrue('default_language' in responce.data)
        self.assertTrue('language' in responce.data)
        self.assertEqual(type(responce.data['language']), list)
        self.assertTrue(len(responce.data['language']) > 0)


    def test_get_price(self):
        responce = client.get(reverse('get_price'))
        self.assertTrue('prices' in responce.data)
        self.assertEqual(type(responce.data['prices']), list)

    def test_get_fonts(self):
        responce = client.get(reverse('get_fonts'))
        self.assertTrue('fonts' in responce.data)
        self.assertEqual(type(responce.data['fonts']), list)
