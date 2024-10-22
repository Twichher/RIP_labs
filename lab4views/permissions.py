from rest_framework import permissions
from .models import AuthUser
import redis
from django.conf import settings
from django.shortcuts import get_object_or_404

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

# class IsManager(permissions.BasePermission):
#     def has_permission(self, request, view):
#         try:
#             username = session_storage.get(request.COOKIES["session_id"])
#             username = username.decode('utf-8') if username else None
#         except:
#             return False
        
#         user = AuthUser.objects.filter(username=username)
#         return bool(user.is_superuser or user.is_staff)

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            username = session_storage.get(request.COOKIES["session_id"])
            username = username.decode('utf-8')
        except:
            return False
        
        user = get_object_or_404(AuthUser,username=username)
        return  bool(user.is_superuser or user.is_staff)