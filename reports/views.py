from django.shortcuts import render
from reservation.models import TripBooking,Booking
from django.shortcuts import get_object_or_404
# Create your views here.


def trip_booking_report(request,pk):
    booking = get_object_or_404(TripBooking, id=pk)
    return render(request, 'reports/trip_booking_report.html', {'booking':booking})

def booking_report(request,pk):
    booking = get_object_or_404(Booking, id=pk)
    return render(request, 'reports/ibooking_report.html', {'booking':booking})