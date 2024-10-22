from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import logging
from django.contrib.auth.hashers import make_password
logger = logging.getLogger(__name__)

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=150)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def __str__(self):
        return f'{self.username}'

    class Meta:
        managed = False
        db_table = 'auth_user'
    
class Spare(models.Model):
    STATUS_CHOICES = [
        (0, 'Действует'),
        (1, 'Удален'),
    ]

    id_spare = models.AutoField(primary_key=True)
    name_spare = models.CharField(max_length=255, verbose_name='Название')
    description_spare = models.TextField(verbose_name='Описание', null=True, blank=True)
    status_spare = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Статус')
    url_spare = models.TextField(max_length=200, verbose_name='URL', null=True, blank=True)
    price_spare = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    
    def __str__(self):
        return self.name_spare
    
    def get_info_spares(self):
        arr = [self.id_spare, self.name_spare, self.description_spare, self.status_spare, self.url_spare, self.price_spare]
        return arr

    class Meta:
        verbose_name = 'Запчасть'
        verbose_name_plural = 'Запчасти'
        db_table = 'Spare'

class Jet_Order(models.Model):
    STATUS_CHOISES = [
        (0, 'Черновик'),
        (1, 'Удален'),
        (2, 'Сформирован'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
    ]

    id_order = models.AutoField(primary_key=True)
    status_order = models.IntegerField(choices=STATUS_CHOISES, default=0, verbose_name='status')
    d_start = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    d_form = models.DateTimeField(verbose_name='Дата формирования', null=True, blank=True)
    d_compl = models.DateTimeField(verbose_name='Дата завершения', null=True, blank=True)
    creater = models.ForeignKey('AuthUser', verbose_name= "Создатель", on_delete=models.DO_NOTHING, null=True, blank=False,related_name='creater')
    adminer = models.ForeignKey('AuthUser', verbose_name= "Модератор", on_delete=models.DO_NOTHING, null=True, related_name='moderator')

    price_order = models.IntegerField(default=0, verbose_name='Цена заказа')
    pick_up_point = models.CharField(max_length=255, verbose_name='Пункт выдачи', null=True, blank=True)

    def __str__(self) -> str:
        return str(self.id_order)

    def get_count_in_order(self):
        itmes = []
        for item in  Jet_Order_Spare.objects.filter(id_order_mm=self):
            itmes.append(item.id_spare_mm)
        return itmes
    
    def get_count_by_count(self):
        items = 0
        for item in  Jet_Order_Spare.objects.filter(id_order_mm=self):
            items += item.count
        return items
    
    def get_price_of_order(self):
        price = 0
        for item in Jet_Order_Spare.objects.filter(id_order_mm=self):
            spare = get_object_or_404(Spare, id_spare = item.id_spare_mm.id_spare)
            price += spare.price_spare * item.count
        return price
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'Order'

class Jet_Order_Spare(models.Model):
    id_order_mm = models.ForeignKey(Jet_Order, on_delete=models.CASCADE)
    id_spare_mm = models.ForeignKey(Spare, on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='Количество', default=0)

    def __str__(self) -> str:
        return f"{self.id_order_mm.id_order} -> {self.id_spare_mm.id_spare}"
    
    class Meta:
        unique_together = (('id_order_mm', 'id_spare_mm'),) 
        verbose_name = "Заказ-Запчасть"
        verbose_name_plural = "Заказы-Запчасти"
        db_table = 'Order_Spare'


