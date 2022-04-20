from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.home, name='home'),
     # Destinations URLS
    path('destinations',views.destination_list.as_view(), name='destination_list'),
    path('destinations/<slug:slug>', views.destination_detail.as_view(),
         name='destination_detail'),

    # Hotels URLS
    path('destinations/<slug:slug>/hotels', views.hotel_list.as_view(),
         name='hotel_list'),
    path('hotels/<slug:slug>', views.hotel_detail.as_view(),
         name='hotel_detail'),

     # Trips URLS
    path('destinations/<slug:slug>/trips/<str:time>', views.trip_list.as_view(),
         name='trip_list'),
    path('hotels/<slug:slug>/trips/<str:time>', views.trip_list_by_hotel.as_view(),
         name='trip_list_by_hotel'),
    path('trips/<int:id>', views.trip_detail.as_view(),
         name='trip_detail'),
    # path('about_us/', views.about_us.as_view(),
    #      name='about_us'),
]