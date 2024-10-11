from .models import *
from rest_framework import serializers


class SpareSerializer(serializers.ModelSerializer):
    #url_spare = serializers.FileField(required=False)

    class Meta:
        # Модель, которую мы сериализуем
        model = Spare
        # Поля, которые мы сериализуем
        fields = ["id_spare", "name_spare", "description_spare", 
                  "status_spare", "url_spare", "price_spare"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ["id", "is_superuser", "username", "password", "last_login", "first_name",
                  "last_name", "email", "is_staff", "is_active", "date_joined"]

    def create(self, validated_data):
        user = AuthUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])  
        user.save()
        return user

class JetOrderSerializer(serializers.ModelSerializer):

    creater = serializers.StringRelatedField(read_only=True)
    adminer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Jet_Order
        fields = ['id_order', 'status_order', 'd_start', 
                  'd_form', 'd_compl', 'creater', 'adminer']
        

class JetOrderSpareSerializer(serializers.ModelSerializer):

    id_order_mm = serializers.StringRelatedField(read_only=True)
    id_spare_mm = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Order_Spare
        fields = ['id_order_mm', 'id_spare_mm', 'count']
    