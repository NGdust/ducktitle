from django.contrib import admin
from .models import Language, Prices, Fonts

admin.site.register(Language)
admin.site.register(Fonts)

@admin.register(Prices)
class PricesAdmin(admin.ModelAdmin):
    pass