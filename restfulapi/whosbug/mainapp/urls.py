from django.conf.urls import include,url
from rest_framework import routers
from mainapp import views
 
# 定义路由地址
# route = routers.DefaultRouter()
 
# 注册新的路由地址
# route.register(r'app' , views.appViewSet)
 
# 注册上一级的路由,访问/api/function 可以获取function加
# urlpatterns = [
#    url('api/', include(route.urls)),
# ]

