from django.urls import path
from .views import CurrentUserView, ChangeEmailView

urlpatterns = [
    path('me/', CurrentUserView.as_view(), name='user_me'),
    path("me/email/", ChangeEmailView.as_view(), name="change_email"),
]