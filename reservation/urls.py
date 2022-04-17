from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations',views.destination_list.as_view(), name='destination_list'),
    path('destinations/<slug:slug>', views.destination_detail.as_view(),
         name='destination_detail'),
    # path('about_us/', views.about_us.as_view(),
    #      name='about_us'),
]