from .models import StoreStatus , TimeZone , MenuHours ,Report
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pytz
import datetime
import pandas as pd
from django.core.cache import cache


# uptime and downtime last day
def trigger( store_id):

    timezone = TimeZone.objects.get(store_id = store_id)


    # this is the local time zone object
    local = pytz.timezone(timezone.timezone)

    # hours.start_time_local
    # hours.end_time_local

    # we will do for the latest day avaiable
    store_status = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()


    date_time_utc_store = store_status.time_stamp_utc

    # gives the weekday number form 0-6
    weekday = date_time_utc_store.weekday()

    open247 = False
    try:
        #this will give 1 object opening and closing time (hopefully)
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()

        # start and end time in local
        start_local = hours.start_time_local
        end_local = hours.end_time_local


        date_time_local_store = date_time_utc_store.astimezone(local)
        # we will assume the latest date we got earlier for combination (for menu hours) (they are in local timezone)
        # latest_store_status date + resturant start time
        start_local_datetime = datetime.datetime.combine(date_time_local_store.date() , start_local)
        end_local_datetime = datetime.datetime.combine(date_time_local_store.date() , end_local)

        # # menu hoursdate time converted to utc
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except (MenuHours.DoesNotExist, TypeError , AttributeError) :
        print("open 247 is true")
        open247 = True

    if open247 is False:
        # print("start" , start_utc)
        # print("end" , end_utc)
        working_hours = end_utc - start_utc
        status_obj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , end_utc))
    else:
        # date = datetime.datetime.strptime(date_time_utc_store ,'%Y-%m-%d %H:%M:%S.%f')
        working_hours = datetime.timedelta(24)
        status_obj = StoreStatus.objects.filter(store = store_id  , time_stamp_utc__date = date_time_utc_store.date())


    observations = {}

    for status in status_obj:
        observations[status.time_stamp_utc] = status.status

    # print(observations)
    uptime , downtime, total = calculate(observations)

    uptime_ratio = uptime/(total)
    downtime_ratio = downtime/(total)
    cache.set('uptime_ratio', uptime_ratio)
    cache.set('downtime_ratio', downtime_ratio)

    return  [uptime_ratio*working_hours , downtime_ratio*working_hours]



def calculate(observations):
    if len(observations) == 0:
        print("no observations between this time")
        return [0,0,0]
    obs = dict(sorted(observations.items()))
    prev = list(obs.values())[0]
    prev_time = list(obs.keys())
    start = prev_time[0]
    end = prev_time[-1]
    prev_time = prev_time[0]
    total = end - start
    # for t in obs.items() :
        # print(t[0].strftime('%H:%M:%S') , t[1])
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
    # print("downtime",downtime)
    return uptime.total_seconds() , downtime.total_seconds() , total.total_seconds()
    # return uptime , downtime , total

def trigger_last_hour(store_id) :
    uptime_ratio = cache.get('uptime_ratio', 0)
    downtime_ratio = cache.get('downtime_ratio', 0)
    return [uptime_ratio*datetime.timedelta(minutes=60) , downtime_ratio*datetime.timedelta(minutes=60)]


# def trigger_last_hour( store_id):

#     timezone = TimeZone.objects.get(store_id = store_id)
#     local = pytz.timezone(timezone.timezone)

#     store = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()
#     date_time_utc_store = store.time_stamp_utc
#     weekday = date_time_utc_store.weekday()

#     open247 = False
#     try:
#         hours = MenuHours.objects.filter(store = store_id , day = weekday).first()

#         # start and end time in local
#         start_local = hours.start_time_local
#         end_local = hours.end_time_local
#         date_time_local_store = date_time_utc_store.astimezone(local)
#         # we will assume the date to be today for combination
#         start_local_datetime = datetime.datetime.combine(date_time_local_store.date() , start_local)
#         end_local_datetime = datetime.datetime.combine(date_time_local_store.date() , end_local)

#         #date time converted to utc
#         start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
#         end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
#         working_hours = end_utc - start_utc
#     except (MenuHours.DoesNotExist, TypeError , AttributeError) :
#         working_hours = datetime.timedelta(hours = 24)
#         open247 = True
#         pass

#     latest_end_time = date_time_utc_store
#     latest_start_time = latest_end_time - datetime.timedelta(hours = 1)

#     if open247:
#         # date = datetime.datetime.strptime(date_time_utc_store ,'%Y-%m-%d %H:%M:%S.%f')
#         # no menu hours given for the restaruant
#         statusObj = StoreStatus.objects.filter(store = store_id  , time_stamp_utc__range = (latest_start_time , latest_end_time))
#     elif start_utc <= latest_start_time and latest_end_time <= end_utc:
#         # the latest time stamp is when the restraunt was open
#         statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (latest_start_time , latest_end_time))
#     elif start_utc <= latest_start_time and latest_end_time > end_utc:
#         # starting time stamp is when the restarunt was open but ending was when it closed
#         statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (latest_start_time , end_utc))
#     elif start_utc > latest_start_time and end_utc > latest_end_time :
#         # here the latest timestamp was  when the restarant was closed so we can't predict anything
#         print("Store was closed last hour so inactive")
#         return  [0 , 0]
#     else:
#         # If the latest timestamp falls between opening and closing times, it fetches store status
#         statusObj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , latest_end_time))
#     print("storeObj" , statusObj[0].time_stamp_utc)
#     observations = {}

#     for status in statusObj:
#         observations[status.time_stamp_utc] = status.status

#     uptime , downtime , total = calculate(observations)
#     if total != 0:
#         uptime_ratio = uptime/total
#         downtime_ratio = downtime/total
#         return [uptime_ratio*working_hours , downtime_ratio*working_hours]
#     return [0,0]




def trigger_last_week( store_id):

    timezone = TimeZone.objects.get(store_id = store_id)
    local = pytz.timezone(timezone.timezone)

    store = StoreStatus.objects.filter(store = store_id).order_by("time_stamp_utc").first()
    date_time_utc_store = store.time_stamp_utc

    # reduce 7 days from the lateset time zone we have
    first_day_week = date_time_utc_store - datetime.timedelta(days = 7)
    # last_day_week = date_time_utc_store

    uptime = datetime.timedelta(0,0,0)
    downtime = datetime.timedelta(0,0,0)
    total = datetime.timedelta(0,0,0)
    working_hours = datetime.timedelta(0,0,0)
    for i in range(0 , 8):
        day = first_day_week + datetime.timedelta(days = i)
        # print(day)
        up  = datetime.timedelta(0 , 0 ,0)
        down = datetime.timedelta(0 , 0 ,0)
        weekday = day.weekday()


        up , down , t , wh = helper_for_week(store_id , weekday , local , day)

        uptime = uptime + datetime.timedelta(seconds = up)
        downtime = downtime + datetime.timedelta(seconds=down)
        total  = total + datetime.timedelta(seconds=t)
        working_hours += wh
        # print(working_hours)

    uptime_ratio = uptime / total
    downtime_ratio = downtime / total


    return  [uptime_ratio*working_hours , downtime_ratio*working_hours]




def helper_for_week(store_id , weekday , local ,date_time_utc_store ):
    open247 = False
    try:
        hours = MenuHours.objects.filter(store = store_id , day = weekday).first()
        start_local = hours.start_time_local
        end_local = hours.end_time_local
        date_time_local_store = date_time_utc_store.astimezone(local)
        start_local_datetime = datetime.datetime.combine(date_time_local_store.date() , start_local)
        end_local_datetime = datetime.datetime.combine(date_time_local_store.date() , end_local)

        #date time converted to utc
        start_utc = local.localize(start_local_datetime).astimezone(pytz.utc)
        end_utc = local.localize(end_local_datetime).astimezone(pytz.utc)
    except (MenuHours.DoesNotExist, TypeError , AttributeError) :
        open247 = True

    if open247 is False:
        # print("start utc " , start_utc)
        # print("end utc " , end_utc)
        working_hours = end_utc - start_utc
        status_obj = StoreStatus.objects.filter(store = store_id , time_stamp_utc__range = (start_utc , end_utc))
    else:
        working_hours = datetime.timedelta(hours = 24)
        status_obj = StoreStatus.objects.filter(store = store_id,time_stamp_utc__date = date_time_utc_store.date())

    observations = {}
    # print(status_obj)
    for status in status_obj:
        observations[status.time_stamp_utc] = status.status

    uptime , downtime ,total = calculate(observations)

    return uptime , downtime , total , working_hours
