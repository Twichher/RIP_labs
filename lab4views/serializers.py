from .models import *
from rest_framework import serializers


class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        write_only_fields = ['password']
        read_only_fields = ['id']

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
    
class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'password']


class UserPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = "__all__"


class SpareSerializer(serializers.ModelSerializer):

    url_spare = serializers.CharField(default="no url", required=False)

    class Meta:

        model = Spare

        fields = "__all__"


class JetOrderSerializer(serializers.ModelSerializer):

    creater = serializers.StringRelatedField(read_only=True)
    adminer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Jet_Order
        fields = "__all__"

class JetOrderInfoSerializer(serializers.ModelSerializer):

    class Meta:

        model = Jet_Order

        fields = ["pick_up_point"]
        

class JetOrderSpareSerializer(serializers.ModelSerializer):

    id_order_mm = serializers.StringRelatedField(read_only=True)
    id_spare_mm = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Jet_Order_Spare
        fields = ['id_order_mm', 'id_spare_mm', 'count']
    

class JetOrderSpareCountSerializer(serializers.ModelSerializer):

    class Meta: 
        model = Jet_Order_Spare
        fields = ['count']