from django.urls import path
from user import views


urlpatterns = [
    path('check/', views.CheckUser.as_view(), name='user-check'),
    path('user_info/', views.InfoUser.as_view(), name='user-info'),
    path('check_jwt/', views.CheckJWT.as_view(), name='jwt-check'),
    path('check_verify_user/', views.CheckVerifyUser.as_view(), name='jwt-check_verify_user'),

    path('login/', views.AuthUser.as_view(), name='user-login'),
    path('login_google/', views.AuthGoogleLogin.as_view(), name='user-login-google'),
    path('verify/', views.VerifyUser.as_view(), name='user-verify'),
    path('retry_send_verify/', views.RetrySendVerify.as_view(), name='user-retry-send-verify'),
    path('user/', views.CreateUser.as_view(), name='user-create'),
    path('update_limit_user/', views.UpdateLimitUser.as_view(), name='update_limit_user'),
    path('change_default_language/', views.ChangeDefaultLanguage.as_view(), name='change_default_language'),

    path('update_pay_user/', views.UpdatePayUser.as_view(), name='update_pay_user'),

    path('update_password/', views.UpdatePassword.as_view(), name='update_password'),
    path('recovery_password/', views.RecoveryPassword.as_view(), name='recovery_password'),
    path('update_user/', views.UpdateUser.as_view(), name='update_user')

]
