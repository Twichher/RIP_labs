from django.shortcuts import render
from .models import Spare, Order, Order_Spare
from django.shortcuts import get_object_or_404
import logging
from django.db import connection
from django.contrib.auth.models import User

# Create your views here.
logger = logging.getLogger(__name__)
price_by_global = 0
price_up_global = 0
from_order_buck = False
order_exist_global = False


def get_spares(id=0, price_by='', price_up=''):
    spares = {
        'spares': [
        ]
    }

    all_spares = Spare.objects.all()
    for spare in all_spares:
        spares['spares'].append(dict(id=spare.id_spare, name_spare=spare.name_spare, price=spare.price_spare, 
                                     img=spare.url_spare, desc=spare.description_spare))
        


    if id != 0:
        return spares['spares'][id-1]
    else:
        new_spares = {
            'spares':[]
        }
        price_by = int(price_by) if price_by.isdigit() else -1
        price_up = int(price_up) if price_up.isdigit() else -1

        global price_by_global, price_up_global
        if price_by >= 0 and price_up >= 0 and price_up >= price_by:
            price_by_global, price_up_global = price_by, price_up
            for var in spares['spares']:
                if var['price'] >= price_by and var['price'] <= price_up: new_spares['spares'].append(var)
        elif price_by >= 0 and price_up == -1:
            price_by_global = price_by
            for var in spares['spares']:
                if var['price'] >= price_by: new_spares['spares'].append(var)
        elif price_up >= 0 and price_by == -1:
            price_up_global = price_up
            for var in spares['spares']:
                if var['price'] <= price_up: new_spares['spares'].append(var)
        elif price_by == -1 and price_up == -1:
            price_by_global, price_up_global = 0, 0
            return spares
    
        return new_spares


def spares(request):

    global from_order_buck, price_by_global, price_up_global, order_exist_global
    if from_order_buck and (price_by_global != 0 or price_up_global != 0):
        if price_by_global != 0 and price_up_global != 0:
            price_by, price_up = price_by_global, price_up_global
        elif price_by_global != 0:
            price_by, price_up = price_by_global, ''
        elif price_up_global != 0:
            price_by, price_up = '', price_up_global

    else:
        price_by, price_up = str(request.GET.get('price_by')), str(request.GET.get('price_up'))


    from_order_buck = False
    my_req = {
        'title': 'spares',
        'spares': get_spares(0, str(price_by), str(price_up))['spares'],
        'id_order': get_last_order(),
        'count_in_order': len(Order_Spare.objects.filter(id_order_mm=get_last_order())),
        'price_by': price_by if price_by != 'None' else '',
        'price_up': price_up if price_up != 'None' else '',
        'order_exist' : order_exist_global,
    }

    #logger.error(f"{request.POST.get('spare_id')}")
    #order_exist_global = True значит был добавлен первый товар в корзину - создалась заявка
    if request.method == "POST" and not order_exist_global:
        order_exist_global = True
        my_req['order_exist'] = True
        new_order = Order(creater = User.objects.filter(is_superuser=False).first())
        new_order.save()
        my_req['id_order'] = get_last_order()
        new_order_spare = Order_Spare(id_order_mm = new_order, id_spare_mm = get_object_or_404(Spare, id_spare=int(request.POST.get('spare_id'))), count=5)
        new_order_spare.save()
        my_req['count_in_order'] = len(Order_Spare.objects.filter(id_order_mm=get_last_order()))
        logger.error(f"{new_order_spare.id} -> {new_order_spare}")

    elif request.method == "POST":
        new_order_spare = Order_Spare(id_order_mm = Order.objects.filter().last(), id_spare_mm = get_object_or_404(Spare, id_spare=int(request.POST.get('spare_id'))), count=5)
        new_order_spare.save()
        my_req['count_in_order'] = len(Order_Spare.objects.filter(id_order_mm=get_last_order()))


    logger.error(f"{Order_Spare.objects.filter(id_order_mm = Order.objects.filter().last())}")

    # if request.method == 'POST' and (not order_exist_global):
    #     new_order = Order()
    #     new_order.save()
    #     new_order_spare = Order_Spare(id_order_mm = new_order, id_spare_mm = get_object_or_404(Spare, id_spare=int(request.POST.get('spare_id'))), count = 1)
    #     new_order_spare.save()
    #     my_req['id_order'] = new_order.id_order
    #     order_exist_global = True
    #     my_req['order_exist'] = order_exist_global
    #     logger.error(f"{my_req['order_exist']} '!!!!'")
    # elif request.method == 'POST' and order_exist_global:
    #     exisitg_order_spare = Order_Spare(id_order_mm = get_object_or_404(Order, id_order=my_req['id_order']), id_spare_mm = get_object_or_404(Spare, id_spare=int(request.POST.get('spare_id'))), count = 1)
    #     exisitg_order_spare.save()
    #     logger.error(f"{my_req['order_exist']} '?????'")

    return render(request, 'spares.html', my_req)

def get_last_order():
    return Order.objects.filter(status_order = 0).last()

def spare(request, id):

    global from_order_buck
    from_order_buck = True

    spare = {
        'title': 'spare',
        'spares': get_spares(id-2),
    }
    

    return render(request, 'spare.html', spare)

def order(request, id):

    global from_order_buck, order_exist_global
    from_order_buck = True

    if request.method == "POST":
        logger.error(request.POST.get('order_id'))
        with connection.cursor() as cursor:
            cursor.execute('UPDATE "Order" SET status_order = 1 WHERE id_order = %s', [int(request.POST.get('order_id'))])
    last_order = get_object_or_404(Order, id_order=id)
    if last_order.status_order == 0:
        logger.error(last_order)
        my_req = {
            'title': 'order',
            'id': id,
            'date_for': last_order.d_start,
            'place_for': 'Ул. Первая, д. 1',
            'items': [],
        }

        inf_order = Order_Spare.objects.filter(id_order_mm = last_order)
        ind = 0
        for var in inf_order:
            my_req['items'].append(get_spares(var.id_spare_mm.id_spare-2))
            my_req['items'][ind]['count'] = var.count
            ind += 1
            #logger.error(var.id_spare_mm.id_spare)
        logger.error(my_req['items'])
    else:
        my_req = {
            'title': 'order',
            'id': id,
            'date_for': "",
            'place_for': "",
            'items': [],
        }

        order_exist_global = False

    return render(request, 'order.html', my_req)
