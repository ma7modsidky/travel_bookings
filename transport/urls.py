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
    path('new_bus',
         views.bus_create.as_view(), name='bus_create'),
    path('select_bus/<int:booking_id>',
         views.bus_select, name='bus_select'),
    path('select_seats/<int:booking_id>/<int:bus_id>',
         views.seats_select, name='seats_select'),
]
