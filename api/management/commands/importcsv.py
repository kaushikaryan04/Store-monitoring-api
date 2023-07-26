# from typing import Any, Optional
from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path
from api.models import TimeZone , MenuHours , StoreStatus

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Command(BaseCommand):
    help = "This I will use to import the menu hours and other csv files "

    def add_arguments(self, parser):
        parser.add_argument('file_name' , help = "file name to add to model")


    def handle(self, *args, **kwargs):
        file_name = kwargs['file_name']
        path = str(BASE_DIR)+"/"+str(file_name)
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            self.stdout.write("File name not correct ")
            return 
        self.stdout.write(f"file_name {file_name}")
        self.stdout.write(f"path {path}")
        if file_name == "store_status.csv":
            for i , row in df.iterrows():
                try:
                    store_activity = StoreStatus(
                        store = TimeZone.objects.get(store_id = row["store_id"]),
                        status = row["status"],
                        time_stamp_utc = row["timestamp_utc"]
                    )
                    self.stdout.write(f"{store_activity.store}  added")
                    store_activity.save()
                except TimeZone.DoesNotExist:
                    # self.stdout.write("we have not added this timezone as the file is huge")
                    store_id = row["store_id"]
                    new_timezone = TimeZone(
                        store_id = store_id,
                        timezone = "America/Chicago"
                    )
                    new_timezone.save()
                    store_activity = StoreStatus(
                        store = TimeZone.objects.get(store_id = store_id),
                        status = row["status"],
                        time_stamp_utc = row["timestamp_utc"]
                    )
                    self.stdout.write("this was not is timezone csv file so we added default timestap as america/chicago")
                    store_activity.save()
                    continue 
        elif file_name == "Menu_hours.csv":
            for i , row in df.iterrows():
                try :
                    menu_hours = MenuHours(
                        store = TimeZone.objects.get(store_id = row["store_id"]),
                        day = row["day"],
                        start_time_local = row["start_time_local"],
                        end_time_local = row["end_time_local"]
                    )
                    self.stdout.write(f"{menu_hours.store} added")
                    menu_hours.save()
                except TimeZone.DoesNotExist:
                    # self.stdout.write("We have not added time zone as this file is huge")
                    store_id = row["store_id"]
                    new_timezone = TimeZone(
                        store_id = store_id,
                        timezone = "America/Chicago"
                    )
                    new_timezone.save()
                    menu_hours = MenuHours(
                        store = TimeZone.objects.get(store_id = store_id),
                        day = row["day"],
                        start_time_local = row["start_time_local"],
                        end_time_local = row["end_time_local"]
                    )
                    self.stdout.write("this was not is timezone csv file so we added default timestap as america/chicago")
                    menu_hours.save()
                    continue
        elif file_name == "timeZoneStores.csv":
            for i , row in df.iterrows():
                timeZone = TimeZone(
                    store_id = row["store_id"],
                    timezone = row["timezone_str"]
                )
                self.stdout.write(f"{timeZone.store_id} added")
                timeZone.save()
        else:
            self.stdout.write("invalid name check file name")
            return 

