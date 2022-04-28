from pyexpat import model
from django import forms
from .models import Trip , TripBooking


class TripBookingForm(forms.ModelForm):
    class Meta:
        model = TripBooking
        fields = '__all__'

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        return super().form_valid(form)

class PayTripBookingForm(forms.Form):
    price = forms.DecimalField(decimal_places=0, disabled=True)
    amount = forms.DecimalField(decimal_places=0)
    
