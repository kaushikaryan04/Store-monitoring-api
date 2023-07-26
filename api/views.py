from .models import StoreStatus , TimeZone , MenuHours
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytz
import datetime


@api_view(["GET"])
def trigger(request , store_id):

    timezone = TimeZone.objects.get(store_id = store_id)
    
    # this is the local time zone object
    local = pytz.timezone(timezone.timezone)

    # hours.start_time_local
    # hours.end_time_local

    # we will do for the latest day avaiable 
    store_status = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()


    date_time_utc_store =store_status.time_stamp_utc

    weekday = date_time_utc_store.weekday() 

    open247 = False
    #this will give 7 objects opening and closing time (hopefully)
    try:
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()
        # start and end time in local
        start_local = hours.start_time_local
        end_local = hours.end_time_local

        # we will assume the date to be today for combination 
        start_local_datetime = datetime.datetime.combine(datetime.date.today() , start_local)
        end_local_datetime = datetime.datetime.combine(datetime.date.today() , end_local)

        #date time converted to utc 
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except MenuHours.DoesNotExist:
        open247 = True 
    
    if open247 is False:
        status_obj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , end_utc))
    else:
        status_obj = StoreStatus.objects.filter(store = store_id)
    
    print(status_obj)




    print("start" , start_utc)
    print("end" , end_utc)






    
    
    
    return Response({store_id : "data"})