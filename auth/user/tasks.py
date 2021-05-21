from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta
from celery import shared_task
from django.utils.timezone import localtime, now
from .models import User

import datetime
import calendar

from django.conf import settings
from loguru import logger

from data.models import Prices


def addMonths(sourcedate, months, time):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    newDate = datetime.datetime(year, month, day, time.hour, time.minute, time.second)
    return newDate

def getTariff(userTarif):
    price = Prices.objects.get(title=userTarif)
    return price.count


@shared_task
def updateLimitVideoUsers():
    users = User.objects.filter(pay_date=localtime(now()).date(), pay_time__gte=localtime(now()).time()).exclude(pay_tariff='Trial')
    for user in users:
        logger.info(f"Update limit video: {user.username}--{user.pay_tariff}")
        user.limit_video = getTariff(user.pay_tariff)
        user.pay_date = addMonths(user.pay_date, 1, user.pay_time)
        user.save()


# @shared_task
# def sendNotification():
#     user = User.objects.get(email='gargan4ukv@yandex.ru')
#     user.sendMail('Привет')
