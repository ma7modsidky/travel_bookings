from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.home, name='home'),
    path('reservations', views.reservations_page, name='reservations_page'),
    path('search_trip_booking', views.search_booking, name='search_booking'),
    path('search_booking', views.search_ibooking, name='search_ibooking'),
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
    path('destinations/<slug:slug>/trips/<str:time>', views.trip_list_by_destination.as_view(),
         name='trip_list_by_destination'),
    path('hotels/<slug:slug>/trips/<str:time>', views.trip_list_by_hotel.as_view(),
         name='trip_list_by_hotel'),
    path('trips/new', views.trip_create.as_view(),
         name='trip_create'),
    path('trips/<int:pk>', views.trip_detail.as_view(),
         name='trip_detail'),
    path('trips/<int:pk>/delete/', views.trip_delete.as_view(),
         name='trip_delete'),
    path('trips/<str:time>', views.trip_list.as_view(),
         name='trip_list'),
     # Bookings
     path('trips/<int:trip_id>/bookings/', views.trip_booking_list.as_view(),
          name='trip_booking_list'),
     path('trips/<int:pk>/bookings/pdf', views.trip_bookings_list_pdf,
          name='trip_bookings_list_pdf'),
     path('trips/booking/new', views.trip_booking_create.as_view(),
          name='trip_booking_create'),
     path('trips/<int:trip_id>/booking/new', views.trip_booking_create.as_view(),
         name='trip_booking_create'),
     path('bookings/<int:pk>', views.trip_booking_detail.as_view(),
          name='trip_booking_detail'),
     path('bookings/<int:pk>/delete', views.trip_booking_delete.as_view(),
          name='trip_booking_delete'),
     path('bookings/<int:pk>/pay', views.trip_booking_pay,
          name='trip_booking_pay'),
     path('bookings/<int:pk>/invoice', views.invoice_pdf,
          name='trip_booking_invoice'),
     path('bookings/<int:pk>/update', views.trip_booking_update.as_view(),
         name='trip_booking_update'),
     path('bookings/<int:pk>/addprogram', views.trip_booking_program_add.as_view(),
          name='trip_booking_program_add'),
     # Hotel Packages
     path('packages/<int:hotel_id>/new', views.package_create.as_view(),
          name='package_create'),
     path('packages/<int:pk>', views.package_detail.as_view(),
          name='package_detail'),
     # individual bookings
     path('ibooking/<int:hotel_id>/<int:package_id>/new', views.booking_create.as_view(),
          name='booking_create'),
     path('ibooking/<int:pk>/detail', views.booking_detail.as_view(),
          name='booking_detail'),
     path('ibooking/<int:package_id>/list', views.booking_list_package.as_view(),
          name='booking_list_package'),
    # path('about_us/', views.about_us.as_view(),
    #      name='about_us'),
    path('ajax/load-hotels/', views.load_hotels, name='ajax_load_hotels'),
]