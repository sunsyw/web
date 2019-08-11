from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPI.as_view()),
    url(r'^usernames/(?P<mobile>1[345789]\d{9})/count/$',views.RegisterPhoneAPI.as_view()),
    url(r'^$',views.RegisterUserTAPI.as_view()),
    url(r'^auths/',obtain_jwt_token),
    url(r'^infos/$',views.UserDetailAPIView.as_view()),
    url(r'^emails/$',views.UserEmailAPIView.as_view()),
    url(r'^emails/verification/$',views.UserEmailVerificationAPIView.as_view()),
    url(r'^addresses/$',views.UserAddressAPIView.as_view()),
    url(r'^addresses/(?P<pk>\d+)/$',views.ChangeAddressAPIView.as_view()),
    url(r'^addresses/(?P<pk>\d+)/title/$',views.AddressTitleAPIView.as_view()),
    url(r'^addresses/(?P<pk>\d+)/status/$',views.AddressStatusAPIView.as_view()),
]
