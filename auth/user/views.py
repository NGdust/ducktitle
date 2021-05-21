import binascii
import calendar
import json
import os
import re
from datetime import datetime

import requests
import jwt
import sendgrid
from django.http import Http404
from loguru import logger
from sendgrid.helpers.mail import *
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_payload_handler, jwt_decode_handler
from .models import User
from data.models import Prices



def sendRegistration(user):
    url = 'http://ducktitle.com/verify/{}/{}/'.format(user.id, user.token)
    msg = 'Подтверждение регистрации. \n' \
          'Перейдите по ссылке: {}'.format(url)
    user.sendMail(msg, 'Подтверждение регистрации')

def sendResetPassword(user):
    msg = 'Привет, {}. \n' \
          'Новый пароль {}\n' \
          'Если же вы не меняли пароль, скорее обратитесь ' \
          'в нашу службу поддержки, и мы вам поможем.'.format(user.email, user.password)
    user.sendMail(msg, 'Пароль изменен')

class CreateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = {}
        data['email'] = request.data['email']
        try:
            data['username'] = request.data['name']
        except:
            data['username'] = request.data['email'].split('@')[0]
        password = request.data['password']
        instance = User.objects.create(**data)
        if password is not None:
            instance.set_password(password)
        instance.token = binascii.hexlify(os.urandom(20)).decode()
        instance.is_active = False
        instance.save()
        requests.get(f'http://index.kvando.tech/video/default/{instance.id}')
        # Text message
        sendRegistration(instance)
        logger.info(f"Create user: {data['username']}")
        return Response({'status': 'verify'}, status=status.HTTP_201_CREATED)


class UpdateUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        jwt_token = request.data.get('jwt_token')
        jwt_data = jwt.decode(jwt_token, verify=False)

        user = get_object_or_404(User, id=jwt_data['user_id'])
        if not user:
            return Response({'status': 'Not verify'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        if email:
            try:
                if not re.search('^[a-z]([\w]+\.?)+(?<!\.)[a-z]@(?!\.)[a-z0-9\.-]+\.?[a-z]{2,}$', email):
                    raise Exception
                _user = get_object_or_404(User, email=email)
                if user.id != _user.id:
                    return Response({'status': 'Email is already occupied'}, status=status.HTTP_403_FORBIDDEN)
            except Http404:
                user.email = email
            except Exception:
                return Response({'status': 'Invalid email!'}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('username')
        if username:
            try:
                if not (re.search('^[a-zA-Z][a-zA-Z0-9_.]+$', username)):
                    raise Exception
                _user = get_object_or_404(User, username=username)
                if user.id != _user.id:
                    return Response({'status': 'Username is already occupied'}, status=status.HTTP_403_FORBIDDEN)
            except Http404:
                user.username = username
            except Exception:
                return Response({'status': 'Invalid username!'}, status=status.HTTP_403_FORBIDDEN)

        user.save()
        return Response({'status': 'Done'}, status=status.HTTP_200_OK)


class RetrySendVerify(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        user.token = binascii.hexlify(os.urandom(20)).decode()
        user.save()
        # Text message
        sendRegistration(user)
        return Response({'status': 'send'}, status=status.HTTP_200_OK)


class AuthGoogleLogin(APIView):
    def post(self, request):
        payload = {'access_token': request.data.get("token")}  # validate the token
        r = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', params=payload)
        data = json.loads(r.text)

        if 'error' in data:
            content = {'message': 'wrong google token / this google token is already expired.'}
            return Response(content)

        # Get or Create user
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            user = User()
            user.email = data['email']
            user.username = data['name']
            user.password = make_password(BaseUserManager().make_random_password())
            user.save()
            requests.get(f'http://index.kvando.tech/video/default/{user.id}')

        #create JWT token
        payload = jwt_payload_handler(user)
        jwt_token = jwt.encode(payload, settings.SECRET_KEY)

        # API response data
        response = {}
        response['name'] = user.username
        response['email'] = user.email
        response['avatar'] = data['picture']
        response['token'] = jwt_token
        logger.info(f"Auth user: {response['name']}")
        return Response(response)

class AuthUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')


            user = get_object_or_404(User, email=email)
            if not user.is_active:
                return Response({'status': 'Not verify'}, status=status.HTTP_403_FORBIDDEN)
            if user and user.check_password(password):
                try:
                    payload = jwt_payload_handler(user)
                    jwt_token = jwt.encode(payload, settings.SECRET_KEY)

                    response = {'name': user.username,
                                'email': user.email,
                                'avatar': user.username,
                                'token': jwt_token}
                    logger.info(f"Auth user: {user.username}")
                    return Response(response, status=status.HTTP_200_OK)

                except Exception as e:
                    raise e
            else:
                response = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                logger.error("Can not authenticate with the given credentials or the account has been deactivated")
                return Response(response, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            res = {'error': 'please provide a email and a password'}
            return Response(res)


class UpdatePassword(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        jwt_token = request.data.get('jwt_token')
        jwt_data = jwt.decode(jwt_token, verify=False)

        email = jwt_data['email']
        password = request.data.get('password')

        user = get_object_or_404(User, email=email)
        if not user:
            return Response({'status': 'Not verify'}, status=status.HTTP_403_FORBIDDEN)

        user.password = make_password(password)
        user.save()
        return Response({'status': 'Done'}, status=status.HTTP_200_OK)


class RecoveryPassword(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')

        user = get_object_or_404(User, email=email)
        if not user:
            return Response({'status': 'Not verify'}, status=status.HTTP_403_FORBIDDEN)
        password = BaseUserManager().make_random_password()
        user.password = make_password(password)
        user.save()
        sendResetPassword(user)
        return Response({'status': 'Done'}, status=status.HTTP_200_OK)


class VerifyUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        id = request.data.get('id')
        token = request.data.get('token')
        user = get_object_or_404(User, id=id)
        if user.token == token:
            user.is_active = True
            user.token = ''
            user.save()
            logger.info(f"User verify: {user.username}")
            return Response({'status': True}, status=status.HTTP_200_OK)
        return Response({'status': False}, status=status.HTTP_200_OK)

class CheckVerifyUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(User, email=email)
        if user.is_active:
            return Response({'status': True}, status=status.HTTP_200_OK)
        return Response({'status': False}, status=status.HTTP_200_OK)


class CheckUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email)
        if user:
            return Response({'status': True}, status=status.HTTP_200_OK)
        return Response({'status': False}, status=status.HTTP_200_OK)

class CheckJWT(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        jwt_token = request.data.get('jwt')
        data = jwt.decode(jwt_token, verify=False)
        end = datetime.fromtimestamp(data['exp'])
        now = datetime.now()
        if now > end:
            user = get_object_or_404(User, email=data['email'])
            if user:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)

                response = {'name': user.username,
                            'email': user.email,
                            'avatar': user.username,
                            'token': token}
                return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({'status': True}, status=status.HTTP_200_OK)

class InfoUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        jwt_token = request.data.get('jwt_token')
        jwt_data = jwt.decode(jwt_token, verify=False)
        user = get_object_or_404(User, id=jwt_data['user_id'])
        data = {
            'pay_tariff': user.pay_tariff,
            'limit_video': user.limit_video
        }
        return Response(data, status=status.HTTP_200_OK)


class UpdateLimitUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        jwt_token = request.data.pop('jwt_token')
        jwt_data = jwt.decode(jwt_token, verify=False)
        user = get_object_or_404(User, id=jwt_data['user_id'])
        user.limit_video -= request.data.get('count')
        user.save()
        logger.info(f"Update limit for: {user.username}")
        return Response({"status": True}, status=status.HTTP_200_OK)

class UpdatePayUser(APIView):
    permission_classes = (permissions.AllowAny,)

    def addDateTime(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        newDate = datetime(year, month, day)
        return newDate

    def getTariff(self, userTarif):
        price = Prices.objects.get(title=userTarif)
        return price.count

    def post(self, request):
        jwt_token = request.data.pop('jwt_token')
        jwt_data = jwt.decode(jwt_token, verify=False)
        user = get_object_or_404(User, id=jwt_data['user_id'])
        user.pay_tariff = request.data['tariff']
        user.pay_date = self.addDateTime(datetime.now(), 1)
        user.pay_time = datetime.now().time()
        user.limit_video = self.getTariff(request.data['tariff'])
        user.save()
        return Response({"status": True}, status=status.HTTP_200_OK)

class ChangeDefaultLanguage(APIView):
    def post(self, request):
        jwt_token = request.data['jwt_token']
        jwt_data = jwt.decode(jwt_token, verify=False)
        language = request.data['default_language']

        user = get_object_or_404(User, id=jwt_data['user_id'])
        user.default_language = language
        user.save()
        logger.info(f"User change default language: {user.username} - {language}")
        return Response({'status': 'Default language changed'})