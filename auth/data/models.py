from django.db import models
import os
from user.models import User


class Language(models.Model):
    country = models.CharField(max_length=100, verbose_name='Страна')
    language = models.CharField(max_length=100, verbose_name='Язык')
    code = models.CharField(max_length=30, verbose_name='Код языка')

    def __str__(self):
        return self.language


class Prices(models.Model):
    desc = models.TextField(verbose_name='Описание')
    plan = models.IntegerField(verbose_name='План в Paddle', default=1)
    count = models.IntegerField(verbose_name='Число видео в месяц', default=1)

    def __str__(self):
        return str(self.plan)



def changeNormalName(instance, *args):
    return f"{instance.path}/{instance.name}/{instance.name}.ttf"
def changeBoldName(instance,*args):
    return f"{instance.path}/{instance.name}/{instance.name}_bold.ttf"
def changeItalicName(instance, *args):
    return f"{instance.path}/{instance.name}/{instance.name}_italic.ttf"

class Fonts(models.Model):
    path = f'fonts/'

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    name = models.CharField(max_length=100, verbose_name='Название', blank=True)
    ttf_normal = models.FileField(upload_to=changeNormalName, verbose_name='Файл шрифта обычный', default='')
    ttf_bold = models.FileField(upload_to=changeBoldName, verbose_name='Файл шрифта жирный', default='')
    ttf_italic = models.FileField(upload_to=changeItalicName, verbose_name='Файл шрифта наклон', default='')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.ttf_normal.name.split('.')[0]
        super(Fonts, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        os.remove(self.ttf_normal.path)
        os.remove(self.ttf_bold.path)
        os.remove(self.ttf_italic.path)
        super(Fonts, self).delete(*args, **kwargs)