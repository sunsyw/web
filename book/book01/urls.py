from django.conf.urls import url
from book01 import views

urlpatterns = [
    url(r'^', views.IndexAPIView.as_view())
]