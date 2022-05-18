from django.urls import path, include
from . import views

app_name= 'reports'

urlpatterns = [
    path('trip_booking_reports/<int:pk>',
         views.trip_booking_report, name='trip_booking_report'),
    path('trip_reports/<int:pk>',
         views.trip_report, name='trip_report'),
    path('ibooking_reports/<int:pk>',
         views.booking_report, name='ibooking_report'),
]