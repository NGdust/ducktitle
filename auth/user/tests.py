import binascii
import json
import os
import datetime

import jwt
from django.conf import settings
from .models import User
from django.test import Client
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.utils import jwt_payload_handler

client = Client()

class TestCreateUser(APITestCase):
    def setUp(self):
        self.email = 'g@g.com'
        self.password = 'test'
        self.username = 'test'

    def test_create(self):
        data = {
            'email': self.email,
            'password': self.password,
            'name': self.username,
        }
        response = client.post(
            reverse('user-create'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class TestReadUser(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@test.com', password='test')
        payload = jwt_payload_handler(self.user)
        self.jwt = jwt.encode(payload, settings.SECRET_KEY)

    def test_login_user(self):
        data = {
            'email': 'testuser@test.com',
            'password': 'test',
        }
        responce = client.post(
            reverse('user-login'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in responce.data)
        self.assertTrue('email' in responce.data)
        self.assertTrue('avatar' in responce.data)
        self.assertTrue('token' in responce.data)

    # def test_verify_user(self):
    #     data = {
    #         'id': self.user.id,
    #         'token': str(self.user.token)
    #     }
    #     responce = client.post(
    #         reverse('user-verify'),
    #         data=json.dumps(data),
    #         content_type='application/json'
    #     )
    #     self.assertEqual(responce.status_code, status.HTTP_200_OK)

    def test_check_jwt(self):
        data = {
            'jwt': self.jwt.decode(),
        }
        responce = client.post(
            reverse('jwt-check'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(responce.status_code, status.HTTP_200_OK)

    def test_check_fail_jwt(self):
        jwt_data = jwt.decode(self.jwt, verify=False)
        exp = datetime.datetime.fromtimestamp(jwt_data['exp']) - datetime.timedelta(days=15)
        user_data = {'user_id': 2, 'username': 'testuser', 'exp': int(exp.timestamp()), 'email': 'testuser@test.com'}
        data = {
            'jwt': jwt.encode(user_data, settings.SECRET_KEY).decode(),
        }
        responce = client.post(
            reverse('jwt-check'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertTrue('name' in responce.data)
        self.assertTrue('email' in responce.data)
        self.assertTrue('avatar' in responce.data)
        self.assertTrue('token' in responce.data)

    def test_check_user(self):
        data = {
            'email': self.user.email,
        }
        responce = client.post(
            reverse('user-check'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertTrue(responce.data['status'])

    def test_info_user(self):
        data = {
            'jwt_token': self.jwt.decode(),
        }
        responce = client.post(
            reverse('user-info'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertTrue('pay_tariff' in responce.data)
        self.assertTrue('limit_video' in responce.data)

    def test_update_limit_user(self):
        data = {
            'jwt_token': self.jwt.decode(),
            'count': 1
        }
        responce = client.post(
            reverse('update_limit_user'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertTrue(responce.data['status'])

    def test_change_default_language(self):
        data = {
            'jwt_token': self.jwt.decode(),
            'default_language': 'en_EN'
        }
        responce = client.post(
            reverse('change_default_language'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(responce.status_code, status.HTTP_200_OK)
        self.assertEqual(responce.data['status'], 'Default language changed')

    def test_update_pay(self):
        data = {
            'jwt_token': self.jwt.decode(),
            'tariff': 'standart'
        }
        responce = client.post(
            reverse('update_pay_user'),
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(responce.status_code, status.HTTP_200_OK)