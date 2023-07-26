from django.contrib import admin
from django.urls import path , include
from .views import trigger

urlpatterns = [
    path("trigger/<int:store_id>/" , trigger)
]