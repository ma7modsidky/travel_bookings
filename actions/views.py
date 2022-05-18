from django.shortcuts import render
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Action
# Create your views here.


class user_actions(LoginRequiredMixin, ListView):
    model = Action
    template_name = 'actions/user_actions.html'
    paginate_by = 15
    redirect_field_name = 'next'

    def get_queryset(self):
        qs = Action.objects.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']= self.request.user
        return context 


class admin_actions(LoginRequiredMixin, ListView):
    model = Action
    template_name = 'actions/admin_actions.html'
    paginate_by = 15
    redirect_field_name = 'next'


