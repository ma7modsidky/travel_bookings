from django.shortcuts import render
from reservation.models import Trip, TripBooking,Booking
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Min, Sum
# Create your views here.


def trip_report(request, pk):
    trip = get_object_or_404(Trip, id=pk)

    persons = trip.bookings.values(
        'adults', 'children').aggregate(total=Sum('adults',)+Sum('children'), extra_seats=Sum('extra_seats'))
    cost = 0
    price = 0
    profit = 0
    rooms = 0
    for b in trip.bookings.all():
        cost += b.get_all_cost
        price += b.get_total_price
        profit += b.get_profit
        rooms += b.get_rooms_count
    return render(request, 'reports/trip_report.html', {'trip': trip, 'persons': persons, 'cost': cost, 'profit': profit, 'price': price , 'rooms_booked':rooms})

def trip_booking_report(request,pk):
    booking = get_object_or_404(TripBooking, id=pk)
    return render(request, 'reports/trip_booking_report.html', {'booking':booking})

def booking_report(request,pk):
    booking = get_object_or_404(Booking, id=pk)
    return render(request, 'reports/ibooking_report.html', {'booking':booking})