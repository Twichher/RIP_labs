from django.shortcuts import render

# Create your views here.

price_by_global = 0
price_up_global = 0
from_order_buck = False


def get_spares(id=0, price_by='', price_up=''):
    spares = {
        'spares': [
            {
                'id':1,
                'name_spare': 'Двигатель бензиновый DLE30',
                'price': 42000,
                'img': 'http://127.0.0.1:9000/rippic/dle30.jpg',
                'desc': 'Бензиновый двигатель от известного производителя моторов DLE, рекомендованный для использования на небольших самолётах.',
            },
            {
                'id':2,
                'name_spare': 'Сервопривод EMAX ES08MDII',
                'price': 1620,
                'img': 'http://127.0.0.1:9000/rippic/emax.jpg',
                'desc': 'Небольшой по размерам и по мощности сервопривод, Futaba/JR-совместимый.',
            },
            {
                'id':3,
                'name_spare': 'Двигатель T-Motor AT4120',
                'price': 11980,
                'img': 'http://127.0.0.1:9000/rippic/t-motor.jpg',
                'desc': 'Бесколлекторный высокоэффективный двигатель, рекомендуемый к использованию с пропеллерами 15"-16".',
            },
            {
                'id':4,
                'name_spare': 'Адаптер для пропеллера',
                'price': 42770,
                'img': 'http://127.0.0.1:9000/rippic/adapter.jpg',
                'desc': 'Алюминиевый адаптер для тянущих пропеллеров. Устанавливается на вал диаметром 5мм. Используется для лопастей с осевым отверстием 3 мм.',
            },
            {
                'id':5,
                'name_spare': 'Двигатель бензиновый DLE60',
                'price': 152380,
                'img': 'http://127.0.0.1:9000/rippic/dle60.jpg',
                'desc': 'Бензиновый двигатель от известного производителя моторов DLE, рекомендованный для использования на больших самолётах, таких как VolJet VT10 и VolJet VT20.',
            },
            {
                'id':6,
                'name_spare': 'Модуль для программ регуляторов',
                'price': 4540,
                'img': 'http://127.0.0.1:9000/rippic/regul.jpg',
                'desc': 'Модуль Hobbywing Program Card предназначен для программирования бесколлекторных регуляторов HobbyWing. Дружественный интерфейс делает программирование ESC простым и быстрым.',
            },
        ]
    }

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

def all_orders():
    orders = { 
        'orders': [
            {
                'id': 1,
                'items': [ 
                    {
                        'info': get_spares(1),
                        'count': 2,
                    }, 
                    {
                        'info': get_spares(2),
                        'count': 5,
                    }, 
                    {
                        'info': get_spares(3),
                        'count': 1,
                    }, 
                        ],
                'date_for': '10.09.2024',
                'place_for': 'Ул. Один, д. 1.',
            }
        ]
    }

    return orders

def spares(request):

    global from_order_buck, price_by_global, price_up_global
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
        'id_order': all_orders()['orders'][0]['id'],
        'count_in_order': len(all_orders()['orders'][0]['items']),
        'price_by': price_by if price_by != 'None' else '',
        'price_up': price_up if price_up != 'None' else '',
    }


    return render(request, 'spares.html', my_req)

def spare(request, id):

    global from_order_buck
    from_order_buck = True

    spare = {
        'title': 'spare',
        'spares': get_spares(id),
    }

    return render(request, 'spare.html', spare)

def order(request, id):

    global from_order_buck
    from_order_buck = True

    my_req = {
        'title': 'order',
        'id': all_orders()['orders'][0]['id'],
        'date_for': all_orders()['orders'][0]['date_for'],
        'place_for': all_orders()['orders'][0]['place_for'],
        'items': all_orders()['orders'][0]['items'],
    }

    return render(request, 'order.html', my_req)