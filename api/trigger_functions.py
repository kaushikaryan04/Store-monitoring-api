from .models import StoreStatus , TimeZone , MenuHours ,Report
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytz
import datetime
import pandas as pd

# uptime and downtime last day
def trigger( store_id):

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
    try:
        #this will give 7 objects opening and closing time (hopefully)        
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()

        # start and end time in local
        start_local = hours.start_time_local
        end_local = hours.end_time_local

        # we will assume the date to be today for combination 
        start_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , start_local)
        end_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , end_local)

        #date time converted to utc 
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except (MenuHours.DoesNotExist, TypeError , AttributeError) :
        open247 = True 
    
    if open247 is False:
        # print("start" , start_utc)
        # print("end" , end_utc)
        status_obj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , end_utc))
    else:
        # date = datetime.datetime.strptime(date_time_utc_store ,'%Y-%m-%d %H:%M:%S.%f')
        status_obj = StoreStatus.objects.filter(store = store_id  , time_stamp_utc__date = date_time_utc_store.date())


    observations = {}

    for status in status_obj:
        observations[status.time_stamp_utc] = status.status
    
    # print(observations)
    uptime , downtime = calculate(observations)

    
    return  [uptime/3600 , downtime/3600]


def calculate(observations):
    if len(observations) == 0:
        print("no observations between this time")
        return [ 0,0]
    obs = dict(sorted(observations.items()))
    prev = list(obs.values())[0]
    prev_time = list(obs.keys())[0]
    uptime = datetime.timedelta(0 , 0 , 0)
    downtime = datetime.timedelta(0 , 0 , 0)
    for o in obs:
        if o == prev_time:
            continue
        if prev == "active" and obs[o] == "active":
            uptime = uptime + (o - prev_time) 
        elif prev == "inactive" and obs[o] == "active" or prev == "active" and obs[o] == "inactive" :
            time = (o - prev_time)/2
            uptime = uptime + time
            downtime = downtime+ time
        else:
            downtime  = downtime + (o - prev_time)
        prev_time = o
        prev = obs[o]
    
    return uptime.total_seconds() , downtime.total_seconds()



def trigger_last_hour( store_id):

    timezone = TimeZone.objects.get(store_id = store_id)
    local = pytz.timezone(timezone.timezone)

    store = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()
    date_time_utc_store = store.time_stamp_utc
    weekday = date_time_utc_store.weekday()
    
    open247 = False
    try:
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()

        # start and end time in local
        start_local = hours.start_time_local
        end_local = hours.end_time_local

        # we will assume the date to be today for combination 
        start_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , start_local)
        end_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , end_local)

        #date time converted to utc 
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except (MenuHours.DoesNotExist, TypeError , AttributeError) :
        open247 = True
        pass

    latest_end_time = date_time_utc_store
    latest_start_time = latest_end_time - datetime.timedelta(hours = 1)

    if open247:
        # date = datetime.datetime.strptime(date_time_utc_store ,'%Y-%m-%d %H:%M:%S.%f')
        statusObj = StoreStatus.objects.filter(store = store_id  , time_stamp_utc__date = date_time_utc_store.date())
    elif start_utc <= latest_start_time and latest_end_time <= end_utc:
        statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (latest_start_time , latest_end_time))
    elif start_utc <= latest_start_time and latest_end_time > end_utc:
        statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (latest_start_time , end_utc))
    elif start_utc > latest_start_time and end_utc > latest_end_time :
        print("Store was closed last hour so inactive")
        return  [0 , 0]
    else:
        statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , latest_end_time))
    
    observations = {}

    for status in statusObj:
        observations[status.time_stamp_utc] = status.status

    uptime , downtime = calculate(observations)

    return  [uptime/60 , downtime/60]




def trigger_last_week( store_id):

    timezone = TimeZone.objects.get(store_id = store_id)
    local = pytz.timezone(timezone.timezone)

    store = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()
    date_time_utc_store = store.time_stamp_utc


    first_day_week = date_time_utc_store - datetime.timedelta(days = 7)
    # last_day_week = date_time_utc_store 

    uptime = 0
    downtime = 0
    
    for i in range(0 , 8):
        day = first_day_week + datetime.timedelta(days = i)
        print(day)
        up  = datetime.timedelta(0 , 0 ,0)
        down = datetime.timedelta(0 , 0 ,0)
        weekday = day.weekday()


        up , down = helper_for_week(store_id , weekday , local , day)
        
        uptime = uptime + up 
        downtime = downtime + down

    
    return  [uptime/3600 , downtime/3600]

    


def helper_for_week(store_id , weekday , local ,date_time_utc_store ):
    open247 = False
    try:
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()
        start_local = hours.start_time_local
        end_local = hours.end_time_local
        start_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , start_local)
        end_local_datetime = datetime.datetime.combine(date_time_utc_store.date() , end_local)

        #date time converted to utc 
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except (MenuHours.DoesNotExist, TypeError , AttributeError) :
        open247 = True 

    if open247 is False:
        print("start utc " , start_utc)
        print("end utc " , end_utc)
        status_obj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , end_utc))
    else:
        status_obj = StoreStatus.objects.filter(store = store_id,time_stamp_utc__date = date_time_utc_store.date())
    
    observations = {}
    print(status_obj)
    for status in status_obj:
        observations[status.time_stamp_utc] = status.status
    
    uptime , downtime = calculate(observations)

    return uptime , downtime
