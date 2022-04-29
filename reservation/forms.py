from pyexpat import model
from tabnanny import verbose
from django import forms
from .models import Trip, TripBooking, TripBookingProgram
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
class TripBookingForm(forms.ModelForm):
    class Meta:
        model = TripBooking
        fields = '__all__'

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        return super().form_valid(form)

class PayTripBookingForm(forms.Form):
    
    amount = forms.DecimalField(label=_('amount'), decimal_places=0)


class TripBookingProgramForm(forms.ModelForm):
    class Meta:
        model = TripBookingProgram
        fields = '__all__'
    # def get_initial(self):
    #     booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
    #     return {
    #         'price': booking.get_total_price(),
    #     }
