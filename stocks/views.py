from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .miniof import *
import logging
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import datetime
from django.utils import timezone
from django.utils.dateparse import parse_datetime

logger = logging.getLogger(__name__)


def get_user():
    return AuthUser.objects.filter(is_superuser = False).first()

def get_admin():
    return AuthUser.objects.filter(is_superuser = True).first()

# Create your views here.

class SpareList(APIView):
    model_class = Spare
    serializer_class = SpareSerializer

    # Возвращает список акций
    #Изменить!!!!!
    def get(self, request, format=None):
        # logger.error(request.user)
        # spares = self.model_class.objects.all().order_by('id_spare')
        # serializer = self.serializer_class(spares, many=True)
        # if str(request.user) == "AnonymousUser":
        #     return Response({"spares": serializer.data,
        #                      "Jet_order": "None"})
        # else:
        #     user = get_object_or_404(AuthUser, username=request.user.username)
        #     order = Jet_Order.objects.filter(creater=user, status_order=0).last()
        #     if order is None:
        #         return Response({"spares": serializer.data,
        #             "Jet_order": "None"})
        #     else:
        #         return Response({"spares": serializer.data,
        #             "Jet_order": order.id_order})

        #получение всех услуг а также их фильтрация + заявка пользователя если есть
        price_by = request.data.get('price_by')
        price_up = request.data.get('price_up')
        logger.error(f"{price_by}, {price_up}")
        if price_by != None and price_up != None and str(price_by).isdigit() and str(price_up).isdigit():
            spares = self.model_class.objects.filter(
                price_spare__gt=price_by,
                price_spare__lt=price_up
            ).order_by('id_spare') #все услуги что есть
        elif price_by != None and str(price_by).isdigit():
            spares = self.model_class.objects.filter(
                price_spare__gt=price_by,
            ).order_by('id_spare')
        elif price_up != None and str(price_up).isdigit():
            spares = self.model_class.objects.filter(
                price_spare__lt=price_up
            ).order_by('id_spare')
        else:
            spares = self.model_class.objects.all().order_by('id_spare')
        serializer = self.serializer_class(spares, many=True)
        order = Jet_Order.objects.filter(creater=get_user(), status_order=0).last() #заказ данного юзера в статусе черновик
        logger.error(order)
        if order is None: 
            return Response({"Jet_order": "null",
                             "Count in Jet_order": 0,
                             "Spares list" : serializer.data})
        else:
            return Response({"Jet_order": order.id_order,
                             "Count in Jet_order": order.get_count_by_count(),
                             "Spares list" : serializer.data})

    # Добавляет новую услугу 
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            spare = serializer.save(url_spare='')
            pic = request.FILES.get("pic_spare")
            if pic is not None:
                pic_result = add_pic(spare, pic)
                if 'error' in pic_result.data:
                    return pic_result
            spare.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #logger.error(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SpareDetail(APIView):
    model_class = Spare
    serializer_class = SpareSerializer


    #Изменить!!!!!  
    def post(self, request, pk, format=None):
        # if str(request.user) == "AnonymousUser":
        #     return Response({"mess":"Не авторизованный пользователь не может добавить запчасть в заказ"})
        # else:
        #     user = get_object_or_404(AuthUser, username=request.user.username)
        #     order = Jet_Order.objects.filter(creater=user, status_order=0).last()
        #     if order is None:
        #         new_order = Jet_Order(
        #             creater = user
        #         )
        #         new_order.save()
        #         new_order_spare = Jet_Order_Spare(
        #             id_order_mm = new_order,
        #             id_spare_mm = get_object_or_404(self.model_class, id_spare = pk),
        #             count = 1
        #         )
        #         new_order_spare.save()
        #         logger.error(new_order.id_order)
        #     else:
        #         logger.error(order.id_order)
        #         new_order_spare = Jet_Order_Spare(
        #             id_order_mm = order,
        #             id_spare_mm = get_object_or_404(self.model_class, id_spare = pk),
        #             count = 1
        #         ) 
        #         new_order_spare.save()

        #     return Response({"mess":"Hello"})

        #добавляет услугу в заявку
        order = Jet_Order.objects.filter(creater=get_user(), status_order=0).last()
        spare = get_object_or_404(self.model_class, id_spare = pk)
        if order is None:
            new_order = Jet_Order(creater = get_user())
            new_order.save()
            new_order_spare = Jet_Order_Spare(
                id_order_mm = new_order,
                id_spare_mm = spare,
                count = 1,
            )
 
        else:
            new_order_spare = Jet_Order_Spare(
                id_order_mm = order,
                id_spare_mm = spare,
                count = 1,
            )

        new_order_spare.save()
        return Response({"Message": f"Добавлено в заказ {spare}"})


    # инф-ия об услуге
    def get(self, request, pk, format=None):
        spare = get_object_or_404(self.model_class, id_spare=pk)
        serializer = self.serializer_class(spare)
        return Response(serializer.data)
    
    # изменение информации об услуге
    def put(self, request, pk, format=None):
        spare = get_object_or_404(self.model_class, id_spare=pk)
        serializer = self.serializer_class(spare, data=request.data, partial=True)
        if 'pic_spare' in serializer.initial_data:
            pic_result = add_pic(spare, serializer.initial_data['pic_spare'])
            if 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # удаление услуги
    def delete(self, requset, pk, format=None):
        spare = get_object_or_404(self.model_class, id_spare=pk)
        if delete_pic(spare):
            spare.delete()
            return Response({"Message":"Spare is deleted"}, status=status.HTTP_204_NO_CONTENT)
        else:
            spare.delete()
            return Response({"Message":"Spare is deleted"})
    

@api_view(["POST"])
def post_new_pic_spare(request, pk, format=None):
    spare = get_object_or_404(Spare, id_spare = pk)
    delete_pic(spare) 
    new_pic = request.FILES.get('pic_spare')
    serializer = SpareSerializer(spare)
    pic_result = add_pic(spare, new_pic)
    if 'error' in pic_result.data:
        return pic_result
    return Response(serializer.data, status=status.HTTP_201_CREATED)

# class UserReg(APIView):

#     model_class = AuthUser
#     serializer_class = UserSerializer

    #создание нового юзера
    #Изменить!!!!! - не нужно
    # def post(self, request, format=None):
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
        
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    #Изменить!!!!!  - не нужно
    # def get(self, request, format=None):
    #     # users = self.model_class.objects.all()
    #     # serializer = self.serializer_class(users, many=True)
    #     user = request.user
    #     try:
    #         user_data = {
    #             "id":user.pk,
    #             "username": user.username,
    #             "email": user.email,
    #             "first_name": user.first_name,
    #             "last_name": user.last_name,
    #             "is_superuser": user.is_superuser,
    #         }
    #         return Response(user_data, status=200)    
    #     except:
    #         return Response({"message: нет авторизованных пользователей"})
    

# class UserLogin(APIView):
#     model_class = AuthUser
#     serializer_class = UserSerializer


#     #Изменить!!!!! - не нужно
#     def post(self, request, format=None):
#         usr = request.data.get('usr')
#         psw = request.data.get('psw')

#         if not usr or not psw:
#             return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(username=usr, password=psw)


#         if user is not None:
#             login(request, user)
#             return Response({'message': 'Успешно аутентифицирован'}, status=status.HTTP_200_OK)
#         else:
#             return Response({'error': 'Неверное имя пользователя или пароль'}, status=status.HTTP_401_UNAUTHORIZED)
        
    # def put(self, requset, username, format=None):
        
        
class UserLogout(APIView):
    model_class = AuthUser
    serializer_class = UserSerializer

    # permission_classes = [IsAuthenticated]

    #Изменить!!!!! - не нужно
    # def post(self, request, format=None):
    #     logout(request)
    #     return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
    
    #Изменить!!!!!
    def put(self, request, format=None):
        user = get_user()
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.error(user.username)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JetOrdersList(APIView):
    model_class = Jet_Order
    serializer_class = JetOrderSerializer

    # permission_classes = [IsAuthenticated]

    #список сформированных заявок данного пользователя
    #Изменить!!!!!
    def get(self, request, format=None):
        find_status = int(request.data.get('status_order', 0))
        find_d_form_by = request.data.get('d_form_by')
        find_d_form_up = request.data.get('d_form_up')      

        if find_status in [2, 3, 4]:
            jetorder = self.model_class.objects.filter(
                Q(status_order=find_status) & Q(creater=get_user())
            )
        else:
            jetorder = self.model_class.objects.filter(
                Q(status_order__gte=2) & Q(creater=get_user())
            )


        if find_d_form_by is not None and parse_datetime(find_d_form_by):
            jetorder = jetorder.filter(d_form__gte = parse_datetime(find_d_form_by))
        
        if find_d_form_up is not None and parse_datetime(find_d_form_up):
            jetorder = jetorder.filter(d_form__lte = parse_datetime(find_d_form_up))


        serializer = self.serializer_class(jetorder, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class JetOrderInfo(APIView):
    model_class = Jet_Order
    serializer_class = JetOrderSerializer

    model_class_2 = Spare
    serializer_class_2 = SpareSerializer

    # permission_classes = [IsAuthenticated]

    #Изменить!!!!!

    #информация об конкретном заказе
    def get(self, request, pk, format=None):
        
        order = get_object_or_404(self.model_class, id_order=pk)
        if order.status_order == 1:
            return Response({"error":"Просмотр удаленных заявок запрещен"})
        else:
            serializer = self.serializer_class(order)
            order_spares = Jet_Order_Spare.objects.all().filter(id_order_mm = order)
            spares = []
            #logger.error(order_spares[1].count) 
            for ordsp in order_spares:
                spare = get_object_or_404(self.model_class_2, id_spare = ordsp.id_spare_mm.id_spare)
                serializer_2 = self.serializer_class_2(spare)
                spares.append({"spare" : serializer_2.data,
                               "count" : ordsp.count})
            if order.status_order in [3, 4]:
                return Response({"data" : serializer.data,
                             "count in order" : order.get_count_by_count(),
                             "price" : order.get_price_of_order(),
                             "spares": spares})
            return Response({"data" : serializer.data,
                             "count in order" : order.get_count_by_count(),
                             "spares": spares})
        
#Изменить!!!!!
#должно работать: измение доп полей заявки(но каких???), 
# сформировать создателем + проверка на обязательные поля(но какие???)
#  завершить - отклонить модером
@api_view(["PUT"])
def put_add_info(request, pk, format=None):
    order = get_object_or_404(Jet_Order, id_order = pk)
    if order.status_order != 0 :
        return Response({"Message" : "заявка не черновик"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    serializer = JetOrderSerializer(order, data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save() 
    return Response(serializer.data)


@api_view(["PUT"])
def put_form_creater(request, pk, format=None):
    order = get_object_or_404(Jet_Order, id_order = pk)
    if order.status_order == 1:
        return Response({"error":"Просмотр удаленных заявок запрещен"})
    if order.status_order == 0 and order.pick_up_point is not None:
        order.status_order = 2
        order.d_form = timezone.now()
        order.save()
        serializer = JetOrderSerializer(order)

        return Response({"Jet order info" : serializer.data,
                         "count" : order.get_count_by_count(),})
                        #  "price" : order.get_price_of_order()})
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # order = get_object_or_404(self.model_class, id_order = pk)
        # if order.status_order == 1:
        #     return Response({"error":"Просмотр удаленных заявок запрещен"})
        
        # if order.creater == get_object_or_404(AuthUser, username = request.user.username):
        #     if request.data.get('status_order') is None:
        #         serializer = self.serializer_class(order, data=request.data)
        #         serializer.is_valid(raise_exception=True)
        #         serializer.save()
        #         return Response(serializer.data)
        #     if int(request.data.get('status_order')) == 2 and order.status_order == 0:
        #         serializer = self.serializer_class(order, data=request.data)
        #         order.d_form = timezone.now()
        #         serializer.is_valid(raise_exception=True)
        #         serializer.save()
        #         return Response(serializer.data)
        #     else:
        #         return Response({"mess":"its not creater or status is incorrect"})
        # elif request.user.is_superuser == True:
        #     #and order.status_order == 2
        #     if int(request.data.get('status_order')) in [3, 4] and order.status_order == 2:
        #         serializer = self.serializer_class(order, data=request.data)
        #         order.d_compl = timezone.now()
        #         adminer =  get_object_or_404(AuthUser, username = request.user.username)
        #         order.adminer = adminer
        #         serializer.is_valid(raise_exception=True) 
        #         serializer.save() 
        #         count_order = len(order.get_count_in_order())
        #         price_order = order.get_price_of_order()
        #         return Response({"data":serializer.data,
        #                         "count_order":count_order,
        #                         "price_order":price_order})
        #     else: 
        #         return Response({"mess":"incorrect data"})
        # else:
        #     return Response({"mess":"It is incorrect user"})
        

@api_view(["PUT"])
def put_from_adminer(request, pk, format=None):
    order = get_object_or_404(Jet_Order, id_order = pk)
    if order.status_order == 1:
        return Response({"error":"Просмотр удаленных заявок запрещен"})
    new_status = request.data.get('status_order', 3)
    if order.status_order == 2 and new_status is not None and str(new_status).isdigit():
        if int(new_status) in [3, 4]:
            order.status_order = new_status
            order.d_compl = timezone.now()
            order.adminer = get_admin()
            order.save()
            serializer = JetOrderSerializer(order)

            return Response({"Jet order" : serializer.data,
                             "Count" : order.get_count_by_count(),
                             "Price" : order.get_price_of_order()})
        else: return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    
# #Изменить!!!!!
@api_view(["DELETE"])
def delete_order(request, pk, format=None):
    order = get_object_or_404(Jet_Order, id_order = pk)

    if order.status_order == 0:
        order.status_order = 1
        order.save()
        return Response({"Message" : "Успешно удалена заявка"}) 
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


@api_view(["POST"])
def register_user(request, format=None):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    
    return Response(serializer.data, status=status.HTTP_201_CREATED)

    # if order.creater == user:
    #     serializer = self.serializer_class(order)
    #     order.status_order = 1
    #     order.d_form = timezone.now()
    #     order.save()
    #     return Response(serializer.data)
    # elif user.is_superuser == True:
    #     serializer = self.serializer_class(order)
    #     order.status_order = 1
    #     order.d_form = timezone.now()
    #     order.adminer = user
    #     return Response(serializer.data)      
    # else:
    #     return Response({"Mess":"Нет доступа"})                  


class JetOrderSpareDetail(APIView):
    model_class = Jet_Order_Spare
    serializer_class = JetOrderSpareSerializer

    # permission_classes = [IsAuthenticated]

    #Изменить!!!!!
    def delete(self, request, opk, spk, format=None):
        order = get_object_or_404(Jet_Order, id_order = opk)
        if order.status_order != 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        spare = get_object_or_404(Spare, id_spare = spk)

        order_spare = get_object_or_404(self.model_class, 
                                        id_order_mm=order,
                                        id_spare_mm=spare)
        
        order_spare.delete()
        return Response({"Mess":f"Запчасть {spare.name_spare} успешно удалена из заказа №{order.id_order}"})
    

    #Изменить!!!!!
    def put(self, request, opk, spk, format=None):
        order = get_object_or_404(Jet_Order, id_order = opk)
        if order.status_order != 0:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        
        spare = get_object_or_404(Spare, id_spare = spk)

        # order_spare = Jet_Order_Spare.objects.filter(id_order_mm=order,
        #                                          id_spare_mm=spare)
        
        #http://localhost:8000/orderspare/9/1/
        order_spare = get_object_or_404(self.model_class, 
                                        id_order_mm=order,
                                        id_spare_mm=spare)

        serializer = self.serializer_class(order_spare, data = request.data, partial=True)
        serializer.is_valid(raise_exception=True) 
        serializer.save() 
        return Response(serializer.data)
    


