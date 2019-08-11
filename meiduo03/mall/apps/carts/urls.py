from django.conf.urls import url
from . import views

urlpatterns = [
    # /cart/
    url(r'^$',views.CartAPIView.as_view(),name='cart'),
]