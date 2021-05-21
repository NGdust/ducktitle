from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'pay_tariff', 'limit_video', 'is_active')
    fields = ('email', 'password', 'username', 'token', 'pay_tariff', 'pay_date', 'pay_time', 'limit_video', 'default_language',
                    'is_active', 'is_superuser')
