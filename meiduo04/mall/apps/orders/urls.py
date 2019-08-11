from django.conf.urls import url
from . import views
from pay.views import PayAPIView

urlpatterns = [
    #/orders/places/
    url(r'^places/$',views.PlaceOrderAPIView.as_view(),name='placeorder'),
    url(r'^$',views.OrderAPIView.as_view(),name='order'),
    # /orders/2.0190315034613e+22/uncommentgoods/
    url(r'^(?P<order_id>\d+)/uncommentgoods/$',views.CommentGoodsAPIView.as_view()),
    url(r'^(?P<order_id>\d+)/comments/$',views.CommentsAPIView.as_view()),
    # /skus/16/comments/
    url(r'^skus/(?P<sku_id>\d+)/comments/$', views.SKUCommentsAPIView.as_view()),
    url(r'^(?P<order_id>\d+)/payment/$', PayAPIView.as_view(),name='pay'),
]