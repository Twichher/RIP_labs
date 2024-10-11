"""
URL configuration for testlr3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from stocks import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),

    path(r'spares/', views.SpareList.as_view(), name='stocks-list'), 
    path(r'spare/<int:pk>/', views.SpareDetail.as_view(), name='spare-detail'),

    path(r'user/reg/', views.UserReg.as_view(), name='user-reg'),
    path(r'user/login/', views.UserLogin.as_view(), name='user-login'),
    path(r'user/logout/', views.UserLogout.as_view(), name='user-logout'),

    path(r'orders/', views.JetOrdersList.as_view(), name='user-logout'),
    path(r'order/<int:pk>/', views.JetOrderInfo.as_view(), name='user-logout'),

    path(r'orderspare/<int:opk>/<int:spk>/', views.JetOrderSpareDetail.as_view(), name='user-logout'),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('accounts/', include('django.contrib.auth.urls')),
]
