"""
URL configuration for lab4set project.

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
from django.urls import include, path
from lab4views import views
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions



schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),  
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    #домен пользователей
    path('user/register/', views.register_user, name='user-reg'), #POST создание нового пользователя
    path('user/login/', views.login_user, name='user-login'), #POST залогиниться
    path('user/logout/', views.logout_user, name='user-logout'), #POST выйти
    path('user/private/', views.private_user, name='user-private'), #PUT личный кабинет
    path('user/whoami/', views.whoami, name='user-whoami'),

    #домен услуг
    path('spares/list/', views.list_spares, name='list-spares'), #get
    path('spares/<int:pk>/info/', views.get_spare, name='get-spare'), #get
    path('spares/<int:pk>/add_info/', views.add_info_spare, name='add-info-spare'), #put
    path('spares/new/', views.new_spare, name='new-spare'), #post
    path('spares/<int:pk>/to_order/', views.to_order_spare, name='to-order-spare'), #post
    path('spares/<int:pk>/add_new_pic/', views.new_pic_spare, name='new-pic-spares'), #post
    path('spares/<int:pk>/delete/', views.delete_spare, name='delete-spares'), #delete
 
    #домен заявок
    path('orders/list/', views.list_orders, name='list-orders'), #get
    path('orders/<int:pk>/info/', views.get_order, name='get-order'), #get
    path('orders/<int:pk>/add_info/', views.add_info_order, name='add-info-orders'), #put
    path('orders/<int:pk>/form_by_creater/', views.form_creater_order, name='form-creater-order'), #put
    path('orders/<int:pk>/form_by_adminer/', views.form_adminer_order, name='form-adminer-order'), #put
    path('orders/<int:pk>/delete/', views.delete_order, name='delete-order'), #delete

    #домен м-м
    path('orderspare/<int:opk>/new_count/<int:spk>/', views.new_count_orderspare, name='new-count-orderspare'), #put
    path('orderspare/<int:opk>/delete/<int:spk>/', views.delete_orderspare, name='delete-orderspare'), #delete
    
    #домен админа
    path('myadmin/all_orders/', views.admin_all_orders, name='admin-all-orders'),
    path('myadmin/all_users/', views.admin_all_users, name='admin-all-users'),
]
