from django.urls import path
from data import views

urlpatterns = [
    path('pars_language/', views.ParsLanguage.as_view(), name='pars_language'),
    path('get_language/', views.GetLanguage.as_view(), name='get_language'),
    path('get_prices/', views.GetPrices.as_view(), name='get_price'),
    path('get_fonts/', views.GetFonts.as_view(), name='get_fonts'),
    path('upload_font/', views.UploadFont.as_view(), name='upload_fonts'),

]
