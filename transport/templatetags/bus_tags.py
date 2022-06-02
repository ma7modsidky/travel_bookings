from django import template
from ..models import Bus, Seat

register = template.Library()


@register.inclusion_tag('transport/seats_1.html')
def show_seats(pk):
 seats = Seat.objects.filter(Bus_id=pk).values_list('number', flat=True)
 bus = Bus.objects.get(id=pk)
 return {'seats': list(seats), 'bus_id': pk , 'buss':bus}

@register.inclusion_tag('transport/seats_1.html')
def booking_seats(pk):
 seats = Seat.objects.filter(booking_id=pk)
 if seats:
    bus = seats[0].Bus 
    seats_num = seats.values_list('number', flat=True)
    return {'seats': list(seats_num), 'bus_id': bus.id, 'buss': bus}

@register.inclusion_tag('transport/seats_2.html')
def seats_form(pk, limit , booking_url):
 bus = Bus.objects.get(id=pk)
 seats = Seat.objects.filter(Bus=bus).values_list('number', flat=True)
 return {'seats': list(seats),'limit':limit , 'booking_url':booking_url}