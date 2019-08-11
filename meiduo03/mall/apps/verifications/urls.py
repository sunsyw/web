from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^imagecodes/(?P<image_code_id>.+)/$', views.RegisterImageCodeAPI.as_view()),
    url(r'^smscodes/(?P<mobile>1[3456789]\d{9})/$', views.RegisterSmsCodeAPI.as_view()),
]