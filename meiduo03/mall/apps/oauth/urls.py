from django.conf.urls import url
from oauth import views

urlpatterns = [
    url(r'^qq/statues/$',views.QQAuthURLAPIView.as_view()),
    url(r'^qq/users/$',views.OauthQQUserAPIView.as_view())
]