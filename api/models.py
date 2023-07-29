from django.db import models
import uuid

class TimeZone(models.Model):
    store_id = models.BigAutoField(primary_key=True)
    timezone = models.CharField(max_length=100)

class MenuHours(models.Model):
    store = models.ForeignKey("TimeZone",on_delete =models.CASCADE)
    day = models.SmallIntegerField()
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

class StoreStatus(models.Model):
    choices = (
        ('active' ,'active'),
        ('inactive' ,'inactive')
    )
    date_time_format = '%Y-%m-%d %H:%M:%S.%f'
    store = models.ForeignKey("TimeZone" , on_delete=models.CASCADE)
    status = models.CharField(max_length=20 , choices=choices)
    time_stamp_utc = models.DateTimeField(auto_now = True)
    class Meta:
        unique_together = ("store" ,"time_stamp_utc") 
    # datetime.datetime(2023, 7, 25, 21, 41, 41, 727209, tzinfo=datetime.timezone.utc)
    # datetime.datetime(year , month , date ,hour ,minute , second , microsecond)

class Report(models.Model):
    report_id = models.UUIDField(primary_key= True , default= uuid.uuid4 ,editable= False)
    store = models.ForeignKey("TimeZone" , on_delete= models.CASCADE)
    uptime_last_week = models.CharField(max_length= 100)
    downtime_last_week = models.CharField(max_length= 100)
    uptime_last_day = models.CharField(max_length=100)
    downtime_last_day = models.CharField(max_length=100)
    uptime_last_hour = models.CharField(max_length=100)
    downtime_last_hour = models.CharField(max_length= 100)
