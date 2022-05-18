from django.urls import path, include
from . import views

app_name = 'actions'

urlpatterns = [
    path('account',
         views.user_actions.as_view(), name='user_actions'),
    path('admin/logs',
         views.admin_actions.as_view(), name='admin_actions'),
]
