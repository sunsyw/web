from django.conf.urls import url
from areas import views
from rest_framework.routers import DefaultRouter


urlpatterns = [
]

# 1 创建路由
router = DefaultRouter()

# 2 注册路由
router.register(r'infos',views.AreaViewSet,base_name='area')

# 3 将router自动生成的url添加到urlpatterns
urlpatterns += router.urls


