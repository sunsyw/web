from django.conf.urls import url
from oauth import views

urlpatterns = [
    url(r'^qq/statues/$',views.QQAuthURLAPIView.as_view()),
    url(r'^qq/users/$',views.OauthQQUserAPIView.as_view()),
    url(r'^weibo/authorization/$',views.WeiboAuthURLLView.as_view()),
    url(r'^sina/user/$',views.WeiboOauthView.as_view()),

]