

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.conf import settings
from django import http
# from django_confirmation_mixin import UpdateConfirmationMixin, CreateConfirmationMixin
import django_filters
from transport.models import Seat
from .models import  Destination, Hotel, HotelPackage, Trip, TripBooking, TripBookingProgram , Booking, TripProgram , AdditionalAmount , Client, PaymentRecord
from django.contrib.auth.mixins import LoginRequiredMixin , PermissionRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta, date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field, HTML
from crispy_tailwind import layout
from .forms import PayTripBookingForm, BookingForm
from django.utils.translation import gettext_lazy as _
from actions.utils import create_action
from account.models import Profile
from django.template.loader import render_to_string
import weasyprint
from django.http import HttpResponse
from .forms import HotelPackageForm

# Create your views here.
BOOKING_STATUS = (('active', 'ACTIVE'), ('cancelled', 'CANCELLED'))

def home(request):
    return render(request, 'reservation/home.html', {})

def reservations_page(request):
    return render(request, 'reservation/misc/reservations_page.html', {})

class destination_list(LoginRequiredMixin, ListView):
    model = Destination
    template_name = 'reservation/destination/destination_list.html'
    paginate_by = 9
    redirect_field_name = 'next'


class destination_detail(LoginRequiredMixin, DetailView,):
    model = Destination
    template_name = 'reservation/destination/destination_detail.html'


class hotel_list(LoginRequiredMixin, ListView):
    model = Hotel
    template_name = 'reservation/hotel/hotel_list.html'
    paginate_by = 12

    def get_queryset(self):
        destination = Destination.objects.get(slug=self.kwargs.get("slug"))
        qs = Hotel.objects.filter(
            destination=destination)
        if self.request.GET.get('query'):
            qs = qs.filter(name__icontains=self.request.GET.get('query'))
        if self.request.GET.get('star'):
            qs = qs.filter(level=self.request.GET.get('star'))  
        return qs    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        destination = Destination.objects.get(slug=self.kwargs.get("slug"))
        hotel_count_all = Hotel.objects.filter(
            destination=destination).count()
        context['destination'] = destination
        context['hotel_count_all'] = hotel_count_all
        return context


class hotel_detail(LoginRequiredMixin, DetailView):
    model = Hotel
    template_name = 'reservation/hotel/hotel_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        hotel = Hotel.objects.get(slug=self.kwargs.get('slug'))
        packages = HotelPackage.objects.filter(hotel=hotel,date_until__gt=date.today())
        context['hotel'] = hotel
        context['packages'] = packages
        return context

class trip_list(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'reservation/trip/trip_list.html'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        time = self.request.GET.get("time")
        sdate = self.request.GET.get("date")
        if sdate:
            qs = qs.filter(
                date_from=sdate)
            return qs
        if time == 'upcoming':
            qs = Trip.objects.filter(
                date_from__gte=date.today())
        elif time == 'previous':
            qs = Trip.objects.filter(
                date_until__lt=date.today())
        elif time == 'ongoing':
            qs = Trip.objects.filter(
                date_from__lte=date.today(), date_until__gte=date.today())
        elif time == 'all':
            qs = Trip.objects.all()
        else:
            qs = qs = Trip.objects.filter(
                date_from__gte=date.today())
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        time = self.request.GET.get("time")
        if self.request.GET.get("date"):
            context['date'] = self.request.GET.get("date")
        context['time'] = time
        return context

def trip_list_by_date(request):
    date = request.GET.get('date')
    trips = Trip.objects.filter(date_from=date)
    paginator = Paginator(trips, 5)
    page = request.GET.get('page')
    try:
        trips = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        trips = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        trips = paginator.page(paginator.num_pages)
    return render(request, 'reservation/trip/trip_list_by_date.html', {
                                                        'date':date,
                                                        'object_list': trips,
                                                        'page': page,
                                                        })
# class trip_list_by_date(LoginRequiredMixin, ListView):
#     model = Trip
#     template_name = 'reservation/trip/trip_list.html'
#     paginate_by = 10

#     def get_queryset(self):
#         qs = super().get_queryset()

# class trip_list_by_time(LoginRequiredMixin, ListView):
#     model = Trip
#     template_name = 'reservation/trip/trip_list.html'
#     paginate_by = 20
#     def get_queryset(self):
#         qs = super().get_queryset()
#         time = self.request.GET.get("time")
#         sdate = self.request.GET.get("date")
#         if sdate:
#             qs = Trip.objects.filter(
#                 date_from=sdate)
#             return qs    
#         if time == 'upcoming':
#             qs = Trip.objects.filter(
#                 date_from__gte=date.today())
#         elif time == 'previous':
#             qs = Trip.objects.filter(
#                 date_until__lt=date.today())
#         elif time == 'ongoing':
#             qs = Trip.objects.filter(
#                 date_from__lte=date.today(), date_until__gte=date.today())
#         elif time == 'all':
#             qs = Trip.objects.all()
#         else:
#             qs = qs = Trip.objects.filter(
#                 date_from__gte=date.today())

#         return qs
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         # Add in a QuerySet of all the books
#         time = self.request.GET.get("time")
#         if self.request.GET.get("date"):
#             context['date'] = self.request.GET.get("date")
#         context['time'] = time
#         return context        


class trip_list_by_destination(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'reservation/trip/trip_list_by_destination.html'
    paginate_by = 15

    def get_queryset(self):
        time = self.request.GET.get("time")
        sdate = self.request.GET.get("date")
        if sdate:
            qs = Trip.objects.filter(
                date_from=sdate)
            return qs
        if time == 'upcoming':
            qs = Trip.objects.filter(
                date_from__gte=date.today())
        elif time == 'previous':
            qs = Trip.objects.filter(
                date_until__lt=date.today())
        elif time == 'ongoing':
            qs = Trip.objects.filter(
                date_from__lte=date.today(), date_until__gte=date.today())
        elif time == 'all':
            qs = Trip.objects.all()
        else:
            qs = qs = Trip.objects.filter(
                date_from__gte=date.today())
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        destination = Destination.objects.get(slug=self.kwargs.get("slug"))
        context['destination'] = destination
        time = self.request.GET.get("time")
        if self.request.GET.get("date"):
            context['date'] = self.request.GET.get("date")
        if self.request.GET.get("time"):
            context['time'] = self.request.GET.get("time")
        return context
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get a context
    #     context = super().get_context_data(**kwargs)
    #     # Add in a QuerySet of all the books
    #     destination = Destination.objects.get(slug=self.kwargs.get("slug"))
    #     context['destination'] = destination
    #     context['time'] = self.kwargs.get("time")
    #     if self.kwargs.get("time") == 'upcoming':
    #         context['object_list'] = Trip.objects.filter(
    #             destination=destination, date_from__gte=timezone.now())
    #     elif self.kwargs.get("time") == 'previous':
    #         context['object_list'] = Trip.objects.filter(
    #             destination=destination, date_until__lt=timezone.now())
    #     elif self.kwargs.get("time") == 'ongoing':
    #         context['object_list'] = Trip.objects.filter(
    #             destination=destination, date_from__lte=timezone.now(), date_until__gte=timezone.now())
    #     else:
    #         context['object_list'] = Trip.objects.filter(
    #             destination=destination)
    #     return context

class trip_list_by_hotel(LoginRequiredMixin, ListView):
    model = Trip
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/trip/trip_list_by_hotel.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        hotel = Hotel.objects.get(slug=self.kwargs.get("slug"))
        context['hotel'] = hotel
        context['destination'] = hotel.destination
        context['time'] = self.kwargs.get("time")
        
        if self.kwargs.get("time") == 'upcoming':
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_from__gte=timezone.now())
        elif self.kwargs.get("time") == 'previous':
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_until__lt=timezone.now())
        elif self.kwargs.get("time") == 'ongoing':
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_from__lte=timezone.now(), date_until__gte=timezone.now())
        else:
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel)
        return context


class trip_create(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Trip
    fields = ['destination', 'accommodation', 'date_from',
              'date_until', 'rooms_total', 'bus_total', 'meeting_location', 'meeting_time', 'transport_price_person', 'single_room_price', 'double_room_price', 'triple_room_price', 'single_room_cost', 'double_room_cost', 'triple_room_cost']
    template_name = 'reservation/trip/trip_create.html'
    exclude = ['creation_user']
    permission_required = ('reservation.add_trip')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Field('destination',
                  css_class='text-center destination'), 'accommodation',
            HTML('<hr class="my-2">'),
            Field('date_from',),
            Field('date_until',),
            HTML('<hr class="my-2">'),
            Fieldset(_('Trip Information'),
                     Row('rooms_total', 'bus_total',
                         css_class='flex flex-row gap-2'),
                     Row('meeting_location', 'meeting_time',
                         css_class='flex flex-row gap-2'),
                     HTML('<hr>'),
                     css_class='my-2'
                     ),
                     
            Fieldset(_('Cost per night'),
                     Row('single_room_cost', 'double_room_cost',
                         'triple_room_cost', css_class='flex flex-row gap-2')
                     ),
            HTML('<hr class="my-2">'),
            Fieldset(_('Price'),
                     Row('transport_price_person'),
                     Row('single_room_price', 'double_room_price',
                         'triple_room_price', css_class='flex flex-row gap-2')
                     ),
        )
        form.helper.label_class = 'dark:text-gray-200'
        # form.helper.Field('date_from',readonly='readonly', id="date_start", template='reservation/datepicker.html')
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        trip = form.save(commit=True)
        verb = _('created trip to')
        create_action(self.request.user,
                      f'{verb} {form.instance.accommodation} ({form.instance.date_from})', trip)
        return super().form_valid(form)
class trip_detail(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'reservation/trip/trip_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['hotel'] = self.get_object().accommodation

        return context


class trip_delete(DeleteView):
    model = Trip
    template_name = "reservation/confirm_delete.html"
    success_url = reverse_lazy('reservation:trip_list', kwargs={'time': 'all'})

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_delete, self).get_object()
        if not obj.creation_user == self.request.user:
            return http.HttpResponseForbidden("Cannot delete other's trips")
        verb = _('Deleted Trip')
        create_action(self.request.user, f'{verb} {obj}', obj)
        return obj

class trip_booking_create(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TripBooking
    fields = ['trip', 'single_room_count', 'double_room_count', 'triple_room_count', 'adults', 'children',
              'extra_seats', 'single_room_persons', 'double_room_persons', 'triple_room_persons', 'name', 'email', 'phone', 'phone2', 'notes', 'discount_percentage', 'discount_amount', 'paid_amount']
    template_name = 'reservation/booking/trip_booking_create.html'
    exclude = ['creation_user']
    permission_required = ('reservation.add_tripbooking')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
                                    Field('trip', css_class='text-center hidden'),
                                    HTML('<hr class="my-2">'),
                                    Row('adults', 'children','extra_seats', css_class='flex flex-row gap-2'),
                                    HTML('<hr class="my-2">'),
                                    Fieldset(_('Numbre of Rooms'),
                                             Row('single_room_count', 'double_room_count',
                                                 'triple_room_count', css_class='flex flex-row gap-2'),
                                             ),
                                    HTML('<hr class="my-2">'),
                                    Fieldset(_('Persons'),
                                             Row('single_room_persons', 'double_room_persons',
                                                 'triple_room_persons', css_class='flex flex-row gap-2')
                                             ),
                                    HTML('<hr class="my-2">'),
                                    Fieldset(_('Personal Detail'),
                                             'name',
                                             'email',
                                             Row('phone', 'phone2',
                                                 css_class='flex flex-row gap-2 w-full')
                                             ),
                                    Field('notes', rows=2),
                                    'discount_percentage', 'discount_amount',
                                    'paid_amount',
                                    )
        form.helper.label_class = 'dark:text-gray-200'
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def get_initial(self):
        if self.kwargs.get('trip_id'):
            trip = get_object_or_404(Trip, id=self.kwargs.get('trip_id'))
            return {
                'trip': trip,
            }

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        try:
            client = Client.objects.get(phone=form.instance.phone)
            form.instance.client = Client.objects.get(
                phone=form.instance.phone)
        except Client.DoesNotExist:
            client = Client.objects.create(
                name=form.instance.name, phone=form.instance.phone, phone2=form.instance.phone2)
            client.save()
            form.instance.client = Client.objects.get(
                phone=form.instance.phone) 
        booking = form.save(commit=True)
        verb = _('made trip booking to')
        create_action(self.request.user,
                      f'{verb} {form.instance.trip}', booking)
        PaymentRecord.objects.create(
            payment_type='tripbooking', amount=form.instance.paid_amount, booking=booking, creation_user=self.request.user)
        # profile = Profile.objects.get(user=self.request.user)
        # profile.balance += form.instance.paid_amount
        # profile.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('trip_id'):
            context['trip'] = get_object_or_404(
                Trip, id=self.kwargs.get('trip_id'))
            return context
        return context

class trip_booking_detail(LoginRequiredMixin, DetailView):
    model = TripBooking
    template_name = 'reservation/booking/trip_booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        context['payForm'] = PayTripBookingForm()
        return context
class trip_booking_delete(DeleteView):
    model = TripBooking
    template_name = "reservation/confirm_delete.html"
    success_url = reverse_lazy('reservation:trip_list', kwargs={'time': 'all'})

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_booking_delete, self).get_object()
        if not obj.creation_user == self.request.user:
            return http.HttpResponseForbidden("Cannot delete other's trips")
        verb = _('permenantly deleted trip booking')    
        create_action(self.request.user, f'{verb} {obj}', obj)
        return obj

class trip_booking_list(LoginRequiredMixin, ListView):
    model = TripBooking
    template_name = 'reservation/booking/trip_booking_list.html'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = Trip.objects.get(id=self.kwargs.get('trip_id'))
        if self.kwargs.get('status') == BOOKING_STATUS[1][0]:
            bookings = TripBooking.objects.filter(
                trip=trip, status=BOOKING_STATUS[1][0])
            context['type'] = 'cancelled'  
        else :        
            bookings = TripBooking.objects.filter(trip=trip , status=BOOKING_STATUS[0][0])
            context['type'] = 'active'
        context['trip'] = trip
        context['bookings'] = bookings
        return context
    
class trip_booking_update(LoginRequiredMixin, UpdateView):
    model = TripBooking
    fields = ['trip', 'single_room_count', 'double_room_count', 'triple_room_count', 'adults', 'children',
              'extra_seats', 'single_room_persons', 'double_room_persons', 'triple_room_persons','name', 'email', 'phone', 'phone2', 'notes']
    template_name = 'reservation/booking/trip_booking_create.html'
    exclude = ['creation_user']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Field('trip', css_class='text-center hidden', ),
            Row('adults', 'children',
                                        'extra_seats', css_class='flex flex-row gap-2'),
                                    Fieldset(_('Numbre of Rooms'),
                                             Row('single_room_count', 'double_room_count',
                                                 'triple_room_count', css_class='flex flex-row gap-2'),

                                             ),


                                    Fieldset(_('Persons'),
                                             Row('single_room_persons', 'double_room_persons',
                                                 'triple_room_persons', css_class='flex flex-row gap-2')
                                             ),

                                    Fieldset(_('Personal Detail'),
                                             'name',
                                             'email',
                                             Row('phone', 'phone2',
                                                 css_class='flex flex-row gap-2 w-full')
                                             ),
                                    'notes',
                                    
                                    )
        form.helper.label_class = 'dark:text-gray-200'
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    

    def form_valid(self, form):
        verb = _('updated trip booking')
        create_action(self.request.user,
                      f'updated trip booking {form.instance}', self.object)
        return super().form_valid(form)

def trip_booking_pay(request , pk):
    booking = get_object_or_404(TripBooking, id=pk)
    if request.method == 'POST':
        form = PayTripBookingForm(data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            booking.paid_amount += form.cleaned_data['amount']
            booking.save()
            verb = _('Recieved amount for trip booking')
            create_action(request.user,
                          f'{verb} {amount}', booking)
            PaymentRecord.objects.create(
                payment_type='tripbooking', amount=form.cleaned_data['amount'], booking=booking, creation_user=request.user)
            # profile = Profile.objects.get(user = request.user)
            # profile.balance += form.cleaned_data['amount']
            # profile.save()
            return redirect(booking)
    else:
        # build form with data provided by the bookmarklet via GET
        form = PayTripBookingForm()
    return render(request, 'reservation/booking/trip_booking_pay.html', {'object':booking,
                                                        'form': form})


def ibooking_pay(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    if request.method == 'POST':
        form = PayTripBookingForm(data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            booking.paid_amount += form.cleaned_data['amount']
            booking.save()
            verb = _('Recieved amount for individual booking')
            create_action(request.user,
                          f'{verb} {amount}', booking)
            PaymentRecord.objects.create(
                payment_type='ibooking', amount=form.cleaned_data['amount'], ibooking=booking, creation_user=request.user)
            # profile = Profile.objects.get(user=request.user)
            # profile.balance += form.cleaned_data['amount']
            # profile.save()
            return redirect(booking)
    else:
        # build form with data provided by the bookmarklet via GET
        form = PayTripBookingForm()
    return render(request, 'reservation/ibooking/ibooking_pay.html', {'object': booking,
                                                                         'form': form})
class trip_booking_program_add(LoginRequiredMixin, CreateView):
    model = TripBookingProgram 
    fields = ['booking', 'program', 'quantity']
    template_name = 'reservation/booking/trip_booking_program_add.html'
   
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(
            TripBooking, id=self.kwargs.get('pk'))
        return context

    def get_initial(self):
        booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
        return {
            'booking': booking,
        }

    def form_valid(self, form):
        booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
        form.instance.unit_price = form.instance.program.price
        form.instance.unit_cost = form.instance.program.cost
        form.instance.unit_name = form.instance.program.name
        verb = _('added trip booking program to')
        create_action(self.request.user,
                      f'{verb} {form.instance.booking}', booking)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('reservation:trip_booking_detail', kwargs={'pk': self.kwargs.get('pk')})

class trip_booking_amounts_add(LoginRequiredMixin, CreateView):
    model = AdditionalAmount
    fields = ['booking', 'price', 'reason']
    template_name = 'reservation/booking/trip_booking_amounts_add.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(
            TripBooking, id=self.kwargs.get('pk'))
        return context

    def get_initial(self):
        booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
        return {
            'booking': booking,
        }

    def form_valid(self, form):
        booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
        verb = _('added trip booking addititonal amount to')
        create_action(self.request.user,
                      f'{verb} {form.instance.booking}', booking)
        return super().form_valid(form)

def invoice_pdf(request,pk):
    booking = get_object_or_404(TripBooking, id=pk)
    html = render_to_string('reservation/pdf/trip_booking_invoice.html',
                            {'object': booking, 'user':request.user})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=booking_{booking.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                           )
    return response


def i_invoice_pdf(request, pk):
    booking = get_object_or_404(Booking, id=pk)
    html = render_to_string('reservation/pdf/ibooking_invoice.html',
                            {'object': booking})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=booking_{booking.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                                                                  )
    return response

def invoice_html(request,pk):
    booking = get_object_or_404(Booking, id=pk)
    return render(request, 'reservation/pdf/ibooking_invoice.html', {'object':booking})

def rooming_list(request,pk):
    trip = get_object_or_404(Trip, id=pk)
    bookings = TripBooking.objects.filter(trip=trip, status='active')
    return render(request, 'reservation/pdf/rooming_list.html', {'trip': trip , 'bookings':bookings})
    
def trip_bookings_list_pdf(request, pk):
    trip = get_object_or_404(Trip, id=pk)
    html = render_to_string('reservation/pdf/booking_list.html',
                            {'object': trip})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=trip_booking_list_{trip.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                                                                  )
    return response


#AJAX
def load_hotels(request): 
    destination = Destination.objects.get(id=request.GET.get(
        'destination_id'))
    hotels = Hotel.objects.filter(
        destination=destination)
    # return render(request, 'persons/city_dropdown_list_options.html', {'cities': cities})
    return JsonResponse(list(hotels.values('id', 'name')), safe=False)


# Individual Booking
class booking_create(LoginRequiredMixin, CreateView):
    model = Booking
    fields = [ 'accommodation_type','transport','transport_price_person' ,'single_room_count','date_from','date_until' ,'double_room_count',  'triple_room_count', 'adults', 'children',
              'extra_seats', 'name', 'email', 'phone', 'notes', 'discount_percentage', 'discount_amount', 'paid_amount']
    template_name = 'reservation/ibooking/create.html'
    exclude = ['creation_user']
    
    # permission_required = ('')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            
            # Row(Field('accommodation',css_class='min-w-[8rem] '), Field('package', css_class='min-w-[8rem] '),
            #     css_class='flex flex-row gap-2',),
            Row('accommodation_type', 
                css_class='flex flex-row gap-4',),
            HTML('<hr class="my-2 ">'),
            'transport',
            'transport_price_person',
            HTML('<p class="my-1 dark:text-white text-xs">(السعر يشمل الذهاب و العودة)</p>'),
            HTML('<hr class="my-2 ">'),
            Row('date_from', 'date_until',
                css_class='flex flex-row gap-4',),
            # Field('date_from'),
            # Field('date_until'),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Numbre of Rooms'),
                     Row('single_room_count', 'double_room_count',
                         'triple_room_count', css_class='flex flex-row gap-2'),
                     ),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Persons'),
                     Row('adults', 'children',
                         'extra_seats', css_class='flex flex-row gap-2'),
                     ),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Personal Detail'),
                     'name',
                     'email',
                     Row('phone',
                         css_class='flex flex-row gap-2 w-full')
                     ),
            Field('notes', rows=2),
            'discount_percentage', 'discount_amount',
            'paid_amount',
        )
        form.helper.legend_class = 'dark:text-white'
        form.helper.label_class = 'dark:text-gray-200'
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def get_initial(self):
        initial = super().get_initial()
        
        initial['accommodation'] = Hotel.objects.get(
            id=self.kwargs.get('hotel_id'))
        initial['package'] = get_object_or_404(
            HotelPackage, id=self.kwargs.get('package_id'))
        return initial


    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        form.instance.accommodation = Hotel.objects.get(
            id=self.kwargs.get('hotel_id'))
        form.instance.package = HotelPackage.objects.get(
            id=self.kwargs.get('package_id'))
        if form.instance.date_from > form.instance.package.date_until or form.instance.date_until > form.instance.package.date_until:
            raise ValidationError(
                _('Booking not in the right dates of the package'))
        try:
            client = Client.objects.get(phone=form.instance.phone)
            form.instance.client = Client.objects.get(
                phone=form.instance.phone)
        except Client.DoesNotExist:
            client = Client.objects.create(
                name=form.instance.name, phone=form.instance.phone)
            client.save()
            form.instance.client = Client.objects.get(
                phone=form.instance.phone)
        booking = form.save(commit=True)
        verb = _('made individual booking to')
        create_action(self.request.user,
                      f'{verb} {form.instance.accommodation}', booking)
        PaymentRecord.objects.create(
            payment_type='ibooking', amount=form.instance.paid_amount, ibooking=booking, creation_user=self.request.user)
        # profile = Profile.objects.get(user=self.request.user)
        # profile.balance += form.instance.paid_amount
        # profile.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['hotel'] = Hotel.objects.get(id=self.kwargs.get('hotel_id'))
        context['package'] = HotelPackage.objects.get(id=self.kwargs.get('package_id'))
        return context
class ibooking_update(LoginRequiredMixin, UpdateView):
    model = Booking
    fields = fields = [ 'accommodation_type', 'transport', 'single_room_count', 'date_from', 'date_until', 'double_room_count',  'triple_room_count', 'adults', 'children',
                       'extra_seats', 'name', 'email', 'phone', 'notes', 'discount_percentage', 'discount_amount', 'paid_amount']
    template_name = 'reservation/ibooking/update.html'
    exclude = ['creation_user']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Row(Field('accommodation', css_class='min-w-[8rem] hidden'), Field('package', readonly='readonly', css_class='min-w-[8rem] hidden'),
                css_class='flex flex-row gap-2',),
            Row('accommodation_type',
                css_class='flex flex-row gap-2'),
            'transport',
            HTML('<hr class="my-2 ">'),
            Field('date_from'),
            Field('date_until'),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Numbre of Rooms'),
                     Row('single_room_count', 'double_room_count',
                         'triple_room_count', css_class='flex flex-row gap-2'),
                     ),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Persons'),
                     Row('adults', 'children',
                         'extra_seats', css_class='flex flex-row gap-2'),
                     ),
            HTML('<hr class="my-2 ">'),
            Fieldset(_('Personal Detail'),
                     'name',
                     'email',
                     Row('phone',
                         css_class='flex flex-row gap-2 w-full')
                     ),
            Field('notes', rows=2),
            'discount_percentage', 'discount_amount',
            'paid_amount',
        )
        form.helper.legend_class = 'dark:text-gray-200'
        form.helper.label_class = 'dark:text-gray-200'
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def form_valid(self, form):
        verb = _('updated individual booking')
        create_action(self.request.user,
                      f'{verb} {form.instance}', self.object)
        return super().form_valid(form)
class package_create(LoginRequiredMixin,PermissionRequiredMixin ,CreateView):
    model = HotelPackage
    template_name = 'reservation/package/create.html'
    permission_required = ('reservation.add_hotelpackage')
    form_class = HotelPackageForm

    def get_context_data(self, **kwargs):
        qs = super().get_context_data(**kwargs)
        qs['hotel'] = get_object_or_404(Hotel, id=self.kwargs.get('hotel_id'))
        return qs


    def get_initial(self):
        creation_user = self.request.user
        return {
            'creation_user': creation_user,
        }
        

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        form.instance.hotel_id = self.kwargs.get('hotel_id')
        package = form.save()
        verb = _('created new package for')
        create_action(self.request.user,
                      f'{verb} {form.instance}', package)
        return super().form_valid(form)

    def form_invalid(self, form):
        print('form invalid')
        print('**' * 5)
        print(form.errors)
        return super().form_invalid(form)




class package_detail(LoginRequiredMixin, DetailView):
    model = HotelPackage
    template_name = 'reservation/package/detail.html'

class package_list(LoginRequiredMixin, ListView):
    model = HotelPackage
    template_name = 'reservation/package/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = Hotel.objects.get(id=self.kwargs.get('pk'))
        context['hotel'] = hotel
        context['time'] = self.request.GET.get("time")
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        time = self.request.GET.get("time")
        if time == 'available':
            qs = qs.filter(
                date_until__gt=date.today())
        elif time == 'not_available':
            qs = qs.filter(
                date_until__lte=date.today())
        else:
            return qs
        return qs   
   

class booking_detail(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'reservation/ibooking/detail.html'

class booking_list_package(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'reservation/ibooking/list.html'

    def get_queryset(self):
        qs = Booking.objects.filter(package=self.kwargs.get('package_id'))
        return qs

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        package = HotelPackage.objects.get(id=self.kwargs.get('package_id'))
        context['package'] = package
        return context


def search_booking(request):
    if TripBooking.objects.filter(id=request.GET.get('trip_booking_id')).exists():
        return redirect(TripBooking.objects.get(id=request.GET.get('trip_booking_id')))
    else:
        return render(request, 'reservation/misc/reservations_page.html', {'no_result': True, 'q': request.GET.get('trip_booking_id')})
    
def search_ibooking(request):
    if Booking.objects.filter(id=request.GET.get('booking_id')).exists():
        return redirect(Booking.objects.get(id=request.GET.get('booking_id')))
    else:
        return render(request, 'reservation/misc/reservations_page.html', {'no_result_i': True, 'q': request.GET.get('booking_id')})


class trip_booking_list_all(LoginRequiredMixin, ListView):
    model = TripBooking
    template_name = 'reservation/misc/trip_booking_list_all.html'
    paginate_by = 10

class booking_list_all(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'reservation/misc/booking_list_all.html'
    paginate_by = 10

class trip_booking_list_user(LoginRequiredMixin, ListView):
    model = TripBooking
    template_name = 'reservation/user/trip_booking_list_user.html'
    paginate_by = 10
    redirect_field_name = 'next'
    def get_queryset(self):
        qs = TripBooking.objects.filter(creation_user=self.request.user)
        return qs

class booking_list_user(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'reservation/user/booking_list_user.html'
    paginate_by = 10
    redirect_field_name = 'next'
    def get_queryset(self):
        qs = Booking.objects.filter(creation_user=self.request.user)
        return qs


class hotel_create(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Hotel
    fields = ['name', 'slug','destination',
              'intro', 'level', 'image', 'available', 'featured']

    template_name = 'reservation/hotel/hotel_create.html'
    permission_required = ('reservation.add_hotel')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.label_class = 'dark:text-gray-200'
        # form.helper.Field('date_from',readonly='readonly', id="date_start", template='reservation/datepicker.html')
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form


class trip_program_create(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TripProgram
    fields = ['name', 'destination', 'cost',
              'price']

    template_name = 'reservation/program/create.html'
    permission_required = ('reservation.add_hotel')
    # success_url = reverse_lazy('account:profile')

    def get_success_url(self):
        if self.kwargs.get('destination_slug'):
            return reverse_lazy('reservation:trip_program_list', kwargs={'destination_slug': self.kwargs['destination_slug']})
        else:
            return reverse_lazy('account:profile')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.label_class = 'dark:text-gray-200'
        # form.helper.Field('date_from',readonly='readonly', id="date_start", template='reservation/datepicker.html')
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def form_valid(self, form):
            verb = _('created trip program')
            create_action(self.request.user,
                        f'{verb} {form.instance}', self.object)
            return super().form_valid(form)
    

class trip_program_edit(LoginRequiredMixin, UpdateView):
    model = TripProgram
    fields = ['name', 'destination', 'cost',
              'price']

    template_name = 'reservation/program/create.html'
    permission_required = ('reservation.add_hotel')
    
    def get_success_url(self):
        slug = self.kwargs['destination_slug']
        return reverse_lazy('reservation:trip_program_list', kwargs={'destination_slug': slug})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.label_class = 'dark:text-gray-200'
        # form.helper.Field('date_from',readonly='readonly', id="date_start", template='reservation/datepicker.html')
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form
    
    def form_valid(self, form):
        verb = _('updated trip program')
        create_action(self.request.user,
                      f'{verb} {form.instance}', self.object)
        return super().form_valid(form)
class trip_program_list(LoginRequiredMixin,ListView):
    model = TripProgram
    template_name = 'reservation/trip_programs/list.html'
    paginate_by = 10
    redirect_field_name = 'next'

    def get_queryset(self):
        d = Destination.objects.get(slug=self.kwargs.get('destination_slug'))
        qs = TripProgram.objects.filter(destination=d)
        return qs

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)    
        context['destination'] = Destination.objects.get(slug=self.kwargs.get('destination_slug'))
        return context

class trip_program_delete(LoginRequiredMixin,PermissionRequiredMixin,DeleteView):
    model = TripProgram
    template_name = "reservation/confirm_delete.html"
    permission_required = ('reservation.add_hotel')
    def get_success_url(self):
        slug = self.kwargs['destination_slug']
        return reverse_lazy('reservation:trip_program_list', kwargs={'destination_slug': slug})
    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_program_delete, self).get_object()
        verb = _('permenantly deleted trip program')    
        create_action(self.request.user, f'{verb} {obj}', obj)
        return obj

def trip_booking_cancel(request,booking_type,pk):
    if booking_type == 'trip_booking':
        booking = get_object_or_404(TripBooking, id=pk)
    elif booking_type == 'ibooking':
        booking = get_object_or_404(Booking, id=pk)
    booking.status = BOOKING_STATUS[1][0]
    if booking_type == 'trip_booking':
        booking.seats_booked = False
        seats = Seat.objects.filter(booking=booking)
        seats.delete()
    elif booking_type == 'ibooking':
        booking.seats_booked = False
        seats = Seat.objects.filter(ibooking=booking)
        seats.delete()
    booking.save()
    return redirect(booking)


def trip_booking_active(request, booking_type, pk):
    if booking_type == 'trip_booking':
        booking = get_object_or_404(TripBooking, id=pk)
    elif booking_type == 'ibooking':
        booking = get_object_or_404(Booking, id=pk)
    booking.status = BOOKING_STATUS[0][0]
    booking.save()
    return redirect(booking)

class client_list(LoginRequiredMixin,ListView):
    model = Client
    template_name = 'reservation/client/list.html'
    paginate_by = 20
    redirect_field_name = 'next'
