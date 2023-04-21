
from django import forms
from .models import Trip, TripBooking, TripBookingProgram ,Booking , HotelPackage , Hotel
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field, HTML
from django.forms import ModelForm, HiddenInput
class TripBookingForm(forms.ModelForm):
    class Meta:
        model = TripBooking
        fields = '__all__'

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        return super().form_valid(form)


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
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

class HotelPackageForm(forms.ModelForm):
    # If you pass FormHelper constructor a form instance
    # It builds a default layout with all its fields
    helper = FormHelper()
    # You can dynamically adjust your layout
    helper.layout = Layout(
        Field('label'),
        Row('date_from', 'date_until', css_class='flex flex-row gap-3'),
        
        HTML('<hr class="my-3">'),
        Fieldset(_(''),
                # SINGLE ROOM / HALF
                 Field('single_room_half_available'),
                 Row('single_room_half_cost', 'single_room_half',
                     css_class='flex flex-row gap-3'),
                 # SINGLE ROOM / FULL
                 Field('single_room_full_available'),
                 Row('single_room_full_cost', 'single_room_full',
                     css_class='flex flex-row gap-3'),
                 HTML('<hr class="my-2">'),
                 # DOUBLE ROOM / HALF
                 Field('double_room_half_available'),
                 Row('double_room_half_cost', 'double_room_half',
                     css_class='flex flex-row gap-3'),
                 # DOUBLE ROOM / FULL
                 Field('double_room_full_available'),
                 Row('double_room_full_cost', 'double_room_full',
                     css_class='flex flex-row gap-3'),
                 HTML('<hr class="my-2">'),
                 # TRIPLE ROOM / HALF
                 Field('triple_room_half_available'),
                 Row('triple_room_half_cost', 'triple_room_half',
                     css_class='flex flex-row gap-3'),
                 # TRIPLE ROOM / FULL
                 Field('triple_room_full_available'),
                 Row('triple_room_full_cost', 'triple_room_full',
                     css_class='flex flex-row gap-3'),
                 ),

    )
    helper.label_class = 'dark:text-gray-200'
    helper.add_input(
        Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))


    # hotel = forms.ModelChoiceField(queryset=Hotel.objects.all(),widget=(attrs={'readonly':'reaadonly'}))
    def __int__(self, *args, **kwargs):
        super(HotelPackageForm, self).__init__(*args, **kwargs)       
        # self.fields['hotel'].widget.attrs.update({'readonly':'readonly'})
       

    class Meta:
        model = HotelPackage
        exclude = ['creation_user']
        fields = ['label', 'date_from', 'date_until',
                  'single_room_half', 'single_room_half_cost', 'single_room_full', 'single_room_full_cost', 'double_room_half', 'double_room_half_cost', 'double_room_full', 'double_room_full_cost', 'triple_room_half', 'triple_room_half_cost', 'triple_room_full', 'triple_room_full_cost',
                  'single_room_half_available', 'single_room_full_available', 'double_room_half_available', 'double_room_full_available', 'triple_room_half_available', 'triple_room_full_available']

        