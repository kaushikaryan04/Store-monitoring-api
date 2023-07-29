from .models import StoreStatus , TimeZone , MenuHours ,Report
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from .trigger_functions import trigger , trigger_last_hour , trigger_last_week

@api_view(["GET"])
def trigger_report(request , store_id):
    a = trigger(store_id)
    b = trigger_last_hour(store_id)
    c = trigger_last_week(store_id)
    uptime_day = a[0]
    downtime_day = a[1]
    uptime_hour = b[0]
    downtime_hour = b[1]
    uptime_week = c[0]
    downtime_week = c[1]
    report = Report(
        store = TimeZone.objects.get(store_id = store_id) ,
        uptime_last_week = uptime_week ,
        downtime_last_week = downtime_week ,
        uptime_last_day = uptime_day ,
        downtime_last_day = downtime_day,
        uptime_last_hour = uptime_hour ,
        downtime_last_hour = downtime_hour
    )
    report.save()
    return Response({"report_id": report.report_id})

@api_view(["GET"])
def get_report(request , report_id):
    report = Report.objects.get(report_id = report_id)
    store_id = report.store.store_id
    uptime_day = report.uptime_last_day
    downtime_day = report.downtime_last_day
    uptime_hour =report.uptime_last_hour
    downtime_hour = report.downtime_last_hour
    uptime_week = report.uptime_last_week
    downtime_week = report.downtime_last_week

    return Response({
        "store_id":store_id,
        "Uptime last day":uptime_day,
        "downtime last day": downtime_day,
        "uptime last hour" : uptime_hour,
        "downtime last hour" : downtime_hour,
        "uptime last week": uptime_week,
        "downtime last week" : downtime_week
    })