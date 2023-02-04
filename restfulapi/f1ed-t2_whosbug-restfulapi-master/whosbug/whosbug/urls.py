from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path,include,re_path
from mainapp import views 
import re
from django.conf.urls import url
# from rest_framework_swagger.views import get_swagger_view

# schema_view = get_swagger_view(title='API 接口文档')

urlpatterns = [
    path('admin/', admin.site.urls),
    # re_path(r'^login/$', 'django.contrib.auth.views.login'),
    path('accounts/login/', LoginView.as_view(template_name='login.html'), name="login"),
    # path('', include('mainapp.urls')), # mainapp.urls里写了api/,意思是这边的空'+api/'
    re_path('api/apps/(?P<pappname>\w+)/commits/(?P<pcommitid>\w+)/', views.getDeleteCommit),
    re_path('api/apps/(?P<pappname>\w+)/commits/', views.getAllCommits),
    re_path('api/commits/(?P<pcommitid>\w+)/', views.getDeleteCommit),
    path('api/commits/', views.getPostCommit),
    path('api/owners/', views.findOwner),
    re_path(r'api/apps/(?P<pappname>\w+)/files/(?P<pfilename>.+)/functions/(?P<pfunctionname>.+)/commits/$', views.getFunctionCommits),
    re_path(r'api/apps/(?P<pappname>\w+)/files/(?P<pfilename>.+)/functions/(?P<pfunctionname>.+)/$', views.getPatchFunction),
    re_path(r'api/apps/(?P<pappname>\w+)/files/(?P<pfilename>.+)/functions/$', views.getAllFunctions),
    re_path(r'api/apps/(?P<pappname>\w+)/files/(?P<pfilename>.+)/$', views.getPatchFile),
    re_path(r'api/apps/(?P<pappname>\w+)/files/$', views.getAllFiles),
    re_path(r'api/apps/(?P<pappname>\w+)/$', views.getPatchApp),
    re_path(r'api/apps/$', views.getAllApps),
]

