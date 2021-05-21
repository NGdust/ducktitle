import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import sendgrid
from sendgrid.helpers.mail import *

class UserAccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email address must be provided')

        if not password:
            raise ValueError('Password must be provided')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    TARIFFS = [
        ('Trial', 'Trial'),
        ('Standart', 'Standart'),
        ('Elite', 'Elite'),
    ]

    objects = UserAccountManager()
    is_active = models.BooleanField('active', default=True)
    is_staff = models.BooleanField('staff', default=False)

    email = models.EmailField('email', unique=True, blank=False, null=False)
    username = models.CharField('username', blank=True, null=True, max_length=400)
    token = models.TextField(verbose_name='Токен подтверждения регистрации', blank=True)
    default_language = models.CharField(verbose_name='Язык по уполчанию', max_length=100, default='en-US')

    limit_video = models.IntegerField(verbose_name='Лимиты видео', default=1)

    pay_tariff = models.CharField(verbose_name='Тариф', max_length=100, choices=TARIFFS, default='Trial')
    pay_date = models.DateField(verbose_name='Дата оплаты', default=datetime.datetime.now().date(), blank=False)
    pay_time = models.TimeField(verbose_name='Время оплаты', default=datetime.datetime.now().time(), blank=False)



    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def sendMail(self, msg, topic):
        # Object with API KEY
        sg = sendgrid.SendGridAPIClient(api_key='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')

        # Settings for sending mail
        from_email = Email("gargan4ukv@yandex.ru")
        to_email = To(self.email)
        content = Content("text/plain", msg)
        mail = Mail(from_email, to_email, topic, content)

        # Send mail
        try:
            sg.client.mail.send.post(request_body=mail.get())
        except Exception as e:
            print(e.body)

    def __unicode__(self):
        return self.email
