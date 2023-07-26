from django.db import models

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
    date_time_format = "%Y-%m-%d %H:%M:%S"
    store = models.ForeignKey("TimeZone" , on_delete=models.CASCADE)
    status = models.CharField(max_length=20 , choices=choices)
    time_stamp_utc = models.DateTimeField(auto_now = True)
    # datetime.datetime(2023, 7, 25, 21, 41, 41, 727209, tzinfo=datetime.timezone.utc)
    # datetime.datetime(year , month , date ,hour ,minute , second , microsecond)