from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .miniof import *
import logging
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
import uuid
from django.conf import settings
from .permissions import *
from django.db.models import Min, Max

logger = logging.getLogger(__name__)
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

@swagger_auto_schema(method='post', request_body=UserRegSerializer)
@api_view(["POST"])
def register_user(request, format=None): 
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        if AuthUser.objects.filter(username = request.data['username']).exists(): 
            return Response({'status': 'Exist'}, status=400)
        serializer = UserRegSerializer(data=request.data) 
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login_user(request):
    try:
        if request.COOKIES["session_id"] is not None:
            return Response({'status': 'Уже в системе'}, status=status.HTTP_403_FORBIDDEN)
    except:
        username = str(request.data["username"]) 
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        logger.error(user)
        if user is not None:
            random_key = str(uuid.uuid4()) 
            session_storage.set(random_key, username)

            response = Response({'status': f'{username} успешно вошел в систему'})
            response.set_cookie("session_id", random_key)

            return response
        else:
            return HttpResponse("{'status': 'error', 'error': 'login failed'}")
    

@permission_classes([IsAuthenticated])
@api_view(["POST"])
def logout_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') if username else None
        logout(request._request)
        logger.error(username)
        response = Response({'Message': f'{username} вышел из системы'})
        response.delete_cookie('session_id')
        return response
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    

@swagger_auto_schema(method='put', request_body=UserPrivateSerializer)
@permission_classes([IsAuthenticated])
@api_view(["PUT"])
def private_user(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') if username else None
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    if not AuthUser.objects.filter(username = username).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = get_object_or_404(AuthUser, username = username)

    serializer = UserPrivateSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()
    logger.error(serializer.data)

    return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def whoami(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') if username else None
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    user = get_object_or_404(AuthUser, username = username)
    serializer = UserPrivateSerializer(user)
    return Response(serializer.data)


@api_view(["GET"])
def list_spares(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') if username else None
    except:
        username = ''
    
    spares = Spare.objects.filter(status_spare=0).order_by('id_spare')
    price_by = request.data.get('price_by') if request.data.get('price_by') is not None else (spares.aggregate(Min('price_spare')))['price_spare__min']
    price_up = request.data.get('price_up') if request.data.get('price_up') is not None else (spares.aggregate(Max('price_spare')))['price_spare__max']
    spares = spares.filter(price_spare__gte=price_by, price_spare__lte=price_up)

    jet_order_id = None
    jet_order_count = 0

    if AuthUser.objects.filter(username = username).exists():
        user = get_object_or_404(AuthUser, username = username)
        if Jet_Order.objects.filter(creater = user, status_order = 0).exists():
            jet_order = get_object_or_404(Jet_Order, creater = user, status_order = 0)
            jet_order_id = jet_order.id_order
            jet_order_count = jet_order.get_count_by_count()


    serializer = SpareSerializer(spares, many=True)
    response = {
        "Jet Order": jet_order_id,
        "Count in Order": jet_order_count,
        "Spares": serializer.data,
    }

    return Response(response)

@api_view(["GET"])
def get_spare(request, pk):
    if Spare.objects.filter(id_spare = pk).exists():
        spare = get_object_or_404(Spare, id_spare = pk)
        if spare.status_spare == 0:
            serializer = SpareSerializer(spare)

            return Response(serializer.data)
    
    return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='put', request_body=SpareSerializer)
@permission_classes([IsAdmin])
@api_view(["PUT"])
def add_info_spare(request, pk):
    if Spare.objects.filter(id_spare = pk).filter(url_spare = 0).exists():
        spare = get_object_or_404(Spare, id_spare = pk)
        serializer = SpareSerializer(spare, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method='post', request_body=SpareSerializer)
@api_view(["POST"])
@permission_classes([IsAdmin])
def new_spare(request):
    serializer = SpareSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["POST"]) 
@permission_classes([IsAuthenticated])
def to_order_spare(request, pk):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8') if username else None
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    if Spare.objects.filter(id_spare = pk).filter(status_spare = 0).exists():
        spare = get_object_or_404(Spare, id_spare = pk)
    else:
        return Response({"Message":"Нет такой запчасти"}, status=status.HTTP_404_NOT_FOUND)
    
    user = get_object_or_404(AuthUser, username=username)

    if Jet_Order.objects.filter(creater = user, status_order = 0).exists():
        order = get_object_or_404(Jet_Order, creater = user, status_order = 0)
    else:
        order = Jet_Order(creater = user)
        order.save()
    
    order_spare = Jet_Order_Spare(
            id_order_mm = order,
            id_spare_mm = spare,
            count = 1
        )
    
    order_spare.save()

    return Response({"Message": f"Добавлено в заказ {spare}"})

 
@api_view(["POST"])
@permission_classes([IsAdmin])
def new_pic_spare(request, pk):
    if Spare.objects.filter(id_spare = pk).filter(status_spare = 0).exists():
        spare = get_object_or_404(Spare, id_spare = pk)
        serializer = SpareSerializer(spare, data=request.data, partial=True)
        if 'pic_spare' in serializer.initial_data:
            pic_result = add_pic(spare, serializer.initial_data['pic_spare'])
            if 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_404_NOT_FOUND)    


@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_spare(request, pk):
    if Spare.objects.filter(id_spare = pk).exists():
        spare = get_object_or_404(Spare, id_spare = pk)
        spare.status_spare = 1
        return Response({"Message":"Spare is deleted"}, status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_404_NOT_FOUND)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def list_orders(request):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    find_d_form_by = request.data.get('d_form_by')
    find_d_form_up = request.data.get('d_form_up')  
    find_status = int(request.data.get('status_order', -1))

    user = get_object_or_404(AuthUser, username = username)
    orders = Jet_Order.objects.filter(creater = user)


    if find_status in [0, 1]:
        return Response({"Message":"Удаленые или черновики просматривать нельзя"})

    if find_status == -1:
        find_status = 2
        orders = orders.filter(status_order__gte = find_status)
    else:
        orders = orders.filter(status_order = find_status)

    if find_d_form_by is not None and parse_datetime(find_d_form_by):
        orders = orders.filter(d_form__gte = parse_datetime(find_d_form_by))
        
    if find_d_form_up is not None and parse_datetime(find_d_form_up):
        orders = orders.filter(d_form__lte = parse_datetime(find_d_form_up))

    serializer = JetOrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_order(request, pk):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    user = get_object_or_404(AuthUser, username = username)
    
    if not Jet_Order.objects.filter(creater = user, id_order = pk).exists():
        return Response({"Message":"Нет такой заявки"})
    
    order = get_object_or_404(Jet_Order, id_order = pk)
    if order.status_order == 1:
        return Response({"Message":"Прсомотр удаленной заявки запрещен"})
    
    serializer = JetOrderSerializer(order)
    order_spares = Jet_Order_Spare.objects.all().filter(id_order_mm = order)
    spares = []
    for ordsp in order_spares:
        spare = get_object_or_404(Spare, id_spare = ordsp.id_spare_mm.id_spare)
        serializer_2 = SpareSerializer(spare)
        spares.append({"spare" : serializer_2.data,
                        "count" : ordsp.count})
    
    return Response({"data" : serializer.data,
                    "count in order" : order.get_count_by_count(),
                    "spares": spares})


@swagger_auto_schema(method='put', request_body=JetOrderInfoSerializer)
@permission_classes([IsAuthenticated])
@api_view(["put"]) 
def add_info_order(request, pk):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    user = get_object_or_404(AuthUser, username = username)
    
    if not Jet_Order.objects.filter(creater = user, id_order = pk).exists():
        return Response({"Message":"Нет такой заявки"})
    
    order = get_object_or_404(Jet_Order, id_order = pk)

    if order.status_order != 0:
        return Response({"Message":"Заявка не черновик"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    serializer = JetOrderInfoSerializer(order, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save() 
 
    return Response(serializer.data)



@permission_classes([IsAuthenticated])
@api_view(["put"]) 
def form_creater_order(request, pk):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    user = get_object_or_404(AuthUser, username = username)
    
    if not Jet_Order.objects.filter(creater = user, id_order = pk).exists():
        return Response({"Message":"Нет такой заявки"})
    
    order = get_object_or_404(Jet_Order, id_order = pk)

    if order.status_order != 0 or order.pick_up_point is None:
        return Response({"Message":"Заявка не черновик либо есть пустые поля"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    order.status_order = 2
    order.d_form = timezone.now()
    order.save()

    serializer = JetOrderSerializer(order)
    return Response({"Jet order info" : serializer.data,
                    "count" : order.get_count_by_count(),})


@api_view(["PUT"])
@permission_classes([IsAdmin])
def form_adminer_order(request, pk):
    username = session_storage.get(request.COOKIES["session_id"])
    username = username.decode('utf-8') 
    user = get_object_or_404(AuthUser, username = username)
    logger.error(user.username)

    if not Jet_Order.objects.filter(id_order = pk).exists():
        return Response({"Message":"Нет такой заявки"})
    
    order = get_object_or_404(Jet_Order, id_order = pk)

    if order.status_order != 2:
        return Response({"Message":"Заявка не сформирована"})
    
    request_status = int(request.data.get("status", 3))

    if request_status not in [3, 4]:
        return Response({"Message":"Неправильно задан статус"})
    
    order.status_order = request_status
    order.d_compl = timezone.now()
    order.adminer = user
    order.price_order = order.get_price_of_order()
    order.save()

    serializer = JetOrderSerializer(order)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_order(request, pk):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    user = get_object_or_404(AuthUser, username = username)
    
    if not Jet_Order.objects.filter(creater = user, id_order = pk).exists():
        return Response({"Message":"Нет такой заявки"})
    
    order = get_object_or_404(Jet_Order, id_order = pk)
    if order.status_order == 0:
        order.status_order = 1
        order.save()
        return Response({"Message":f"Заявка {order} удалена"})
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@swagger_auto_schema(method='put', request_body=JetOrderSpareCountSerializer)  
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def new_count_orderspare(request, opk, spk, format=None):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    user = get_object_or_404(AuthUser, username=username)

    if not Jet_Order.objects.filter(creater = user, id_order = opk, status_order = 0).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    order = get_object_or_404(Jet_Order, id_order = opk)

    spare = get_object_or_404(Spare, id_spare = spk)

    order_spare = get_object_or_404(Jet_Order_Spare,
                                    id_order_mm = order, 
                                    id_spare_mm = spare)
    
    serializer = JetOrderSpareCountSerializer(order_spare, data = request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_orderspare(request, opk, spk, format=None):
    try:
        username = session_storage.get(request.COOKIES["session_id"])
        username = username.decode('utf-8')
    except:
        return Response({"Message":"Нет авторизованных пользователей"})
    
    user = get_object_or_404(AuthUser, username=username)

    if not Jet_Order.objects.filter(creater = user, id_order = opk, status_order = 0).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    order = get_object_or_404(Jet_Order, id_order = opk)

    spare = get_object_or_404(Spare, id_spare = spk)

    order_spare = get_object_or_404(Jet_Order_Spare,
                                    id_order_mm = order, 
                                    id_spare_mm = spare)

    order_spare.delete()
    return Response({"Mess":f"Запчасть {spare.name_spare} успешно удалена из заказа №{order.id_order}"})

@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_all_orders(request):
    orders = Jet_Order.objects.filter(status_order__gt = 0)
    serializer = JetOrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAdmin])
def admin_all_users(request):
    users = AuthUser.objects.all()
    serializer = UserPrivateSerializer(users, many=True)
    return Response(serializer.data)