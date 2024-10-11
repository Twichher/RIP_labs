from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Spare)
admin.site.register(Jet_Order)
admin.site.register(Order_Spare)