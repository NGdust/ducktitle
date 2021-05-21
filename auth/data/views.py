import json
import os

import jwt
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from rest_framework import status
from user.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Language, Prices, Fonts
from django.conf import settings

class ParsLanguage(APIView):
    def get(self, request):
        for item in Language.objects.all():
            item.delete()
        with open(os.getcwd() + "/data/languages.html", "r") as f:
            contents = f.read()

            soup = BeautifulSoup(contents, 'lxml')
            for tag in soup.find_all("li"):
                language = tag.text.split(' ')[0]
                code = tag['data-value']
                try:
                    country = tag.text.split(' ')[1].replace('(', '').replace(')', '')
                except:
                    country = ''
                Language.objects.create(language=language, country=country, code=code)

        response = {'status': 'Done'}
        return Response(response)


class GetLanguage(APIView):
    def post(self, request):
        jwt_token = request.data['jwt_token']
        jwt_data = jwt.decode(jwt_token, verify=False)
        response = {
            'language': []
        }
        user = get_object_or_404(User, id=jwt_data['user_id'])
        response['default_language'] = user.default_language

        langs = Language.objects.all()
        for item in langs:
            if item.country:
                country = ' ({})'.format(item.country)
            else:
                country = ''
            response['language'].append(
                {
                    'id': item.id,
                    'code': item.code,
                    'title': '{}{}'.format(item.language, country),
                }
            )
        response['default_language'] = user.default_language
        return Response(response)


class GetPrices(APIView):
    basePaddleUrl = "https://vendors.paddle.com/api/2.0"
    plansUrl = "/subscription/plans"
    couponsUrl = "/product/list_coupons"

    def get(self, request):
        response = {}
        prices = Prices.objects.all()

        response['prices'] = []
        for i, v in enumerate(prices):
            products = json.loads(requests.post(url=self.basePaddleUrl + self.plansUrl, data={
                "vendor_id": settings.PADDLE_VENDOR_ID,
                "vendor_auth_code": settings.PADDLE_VENDOR_CODE,
                "plan": v.plan
            }).text)

            coupons = json.loads(requests.post(url=self.basePaddleUrl + self.couponsUrl, data={
                "vendor_id": settings.PADDLE_VENDOR_ID,
                "vendor_auth_code": settings.PADDLE_VENDOR_CODE,
                "product_id": v.plan
            }).text)
            response['prices'].append({
                "id": v.plan,
                "title": products['response'][0]['name'],
                "desc": json.loads(v.desc),
                "price": products['response'][0]['recurring_price']['USD'],
                "coupons": coupons['response'],
                "count": v.count
            })
        return Response(response, status=status.HTTP_200_OK)




class GetFonts(APIView):
    def get(self, request):
        response = {
            'fonts': []
        }
        mediaPath = 'media/'
        fonts = Fonts.objects.all()
        for font in fonts:
            if not font.is_active: continue
            response['fonts'].append(
                {
                    'name': font.name,
                    'url': mediaPath + font.ttf_normal.name,
                }
            )
        return Response(response)

    def post(self, request):
        jwt_token = request.data['jwt_token']
        jwt_data = jwt.decode(jwt_token, verify=False)

        response = {
            'fonts': []
        }
        mediaPath = 'media/'
        fonts = Fonts.objects.filter(Q(user=None) | Q(user__email=jwt_data["email"]))
        for font in fonts:
            if not font.is_active: continue
            response['fonts'].append(
                {
                    'name': font.name,
                    'url': mediaPath + font.ttf_normal.name,
                }
            )
        return Response(response)


class UploadFont(APIView):
    def post(self, request):
        font_normal = request.FILES['font_normal']
        font_bold = request.FILES['font_bold']
        font_italic = request.FILES['font_italic']
        jwt_token = request.data['jwt_token']
        jwt_data = jwt.decode(jwt_token, verify=False)

        user = User.objects.get(email=jwt_data["email"])
        Fonts.objects.create(user=user, ttf_normal=font_normal, ttf_bold=font_bold, ttf_italic=font_italic)

        return Response({"status": "upload"})
