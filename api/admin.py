from django.contrib import admin
from .models import Report, TimeZone , MenuHours , StoreStatus
# Register your models here.
admin.site.register(TimeZone)
admin.site.register(MenuHours)
admin.site.register(StoreStatus)
admin.site.register(Report)
