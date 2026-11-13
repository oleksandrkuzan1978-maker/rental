from django.urls import  path
from .views import (RegisterView
                    , LoginView
                    , RefreshView
                    , LogoutView
                    , LogoutAllView
                    , ChangePasswordView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout-all/', LogoutAllView.as_view(), name='logout_all'), # выход со всех устройств, на которых юзер залогинился
    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),
    path('password/change/', ChangePasswordView.as_view(), name='password_change'),
]