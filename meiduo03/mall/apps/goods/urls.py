from django.conf.urls import url
from . import views

urlpatterns = [
    #/goods/categories/
    url(r'^categories/(?P<category_id>\d+)/hotskus/$',views.HotsSKUListAPIView.as_view()),
    #/goods/categories/(?P<category_id>\d+)/hotskus/
    url(r'^categories/(?P<category_id>\d+)/skus/$',views.SKUListAPIView.as_view()),

]

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register('search', views.SKUSearchViewSet, base_name='skus_search')

urlpatterns += router.urls