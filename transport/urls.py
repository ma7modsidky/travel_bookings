from django.urls import path, include
from . import views

app_name = 'transport'

urlpatterns = [
    path('bus_list',
         views.bus_list.as_view(), name='bus_list'),
    path('bus_list/<str:type>',
         views.bus_list.as_view(), name='bus_list'),
    path('bus_detail/<int:pk>',
         views.bus_detail.as_view(), name='bus_detail'),
    path('bus_detail/<int:pk>/delete',
         views.bus_delete.as_view(), name='bus_delete'),
    path('new_bus',
         views.bus_create.as_view(), name='bus_create'),
    path('select_seats/bus_only/<int:booking_id>/<int:bus_id>',
         views.seats_select_other, name='seats_select_other'),
    path('select_bus/<str:booking_type>/<int:booking_id>',
         views.bus_select, name='bus_select'),
    path('select_seats/<str:booking_type>/<int:booking_id>/<int:bus_id>',
         views.seats_select, name='seats_select'),
    
    path('bus_detail/<int:bus_id>/bookings/<str:seat_type>',
         views.bus_bookings, name='bus_bookings'),
    path('bus_detail/<int:bus_id>/bookings/<str:seat_type>/print',
         views.bus_booking_html, name='bus_booking_html'),
     # Bus only bookings    
     path('new_bus_booking/<int:bus_id>',
          views.bus_only_booking_create.as_view(), name='bus_only_booking_create'),
     path('bus_booking/<int:pk>',
          views.bus_only_booking_detail.as_view(), name='bus_only_booking_detail'),
]
