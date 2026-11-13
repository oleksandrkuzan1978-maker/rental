from os import name

from django.contrib.auth.views import PasswordChangeView
from django.urls import  path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import RegisterView, LoginView, RefreshView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('logout-all/', , name='logout_all'), # выход со всех устройств, на которых юзер залогинился
    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),
    # path('password/change/', PasswordChangeView.as_view(), name='password_change'),
]