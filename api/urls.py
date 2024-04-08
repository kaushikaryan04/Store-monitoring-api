from django.urls import path
from .views import trigger_report ,get_report , get_most_records_store_id

urlpatterns = [
    # path("trigger/<int:store_id>/" , trigger),
    # path("triggerday/<int:store_id>/" , trigger_last_hour),
    # path("triggerweek/<int:store_id>/" , trigger_last_week ),
    path("trigger_report/<int:store_id>/" , trigger_report),
    path("get_report/<str:report_id>/" , get_report),
    path("getmostrecords" ,get_most_records_store_id )
]
