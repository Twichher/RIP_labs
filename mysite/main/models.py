from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
import logging
logger = logging.getLogger(__name__)
    
class Spare(models.Model):
    STATUS_CHOICES = [
        (0, 'Действует'),
        (1, 'Удален'),
    ]

    id_spare = models.AutoField(primary_key=True)
    name_spare = models.CharField(max_length=255, verbose_name='Название')
    description_spare = models.TextField(verbose_name='Описание', null=True, blank=True)
    status_spare = models.IntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Статус')
    url_spare = models.URLField(max_length=200, verbose_name='URL', null=True, blank=True)
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

class Order(models.Model):
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
    creater = models.ForeignKey(User, verbose_name= "Создатель", on_delete=models.CASCADE, null=True, related_name='creater')
    adminer = models.ForeignKey(User, verbose_name= "Модератор", on_delete=models.CASCADE, null=True, related_name='moderator')

    def __str__(self) -> str:
        return str(self.id_order)

    def get_count_in_order(self):
        itmes = []
        for item in  Order_Spare.objects.filter(id_order_mm=self):
            itmes.append(item.id_spare_mm)
        return itmes
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        db_table = 'Order'

class Order_Spare(models.Model):
    id_order_mm = models.ForeignKey(Order, on_delete=models.CASCADE)
    id_spare_mm = models.ForeignKey(Spare, on_delete=models.CASCADE)

    count = models.IntegerField(verbose_name='Количество', default=0)

    def __str__(self) -> str:
        return f"{self.id_order_mm.id_order} -> {self.id_spare_mm.id_spare}"
    
    class Meta:
        unique_together = (('id_order_mm', 'id_spare_mm'),) 
        verbose_name = "Заказ-Запчасть"
        verbose_name_plural = "Заказы-Запчасти"
        db_table = 'Order_Spare'

