# import jsonfield
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta ,date
# Create your models here.


def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]


class Destination(models.Model):
    name = models.CharField(max_length=25, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    intro = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/destination', blank=True)
    # def get_absolute_url(self):
    #     return reverse('app:developer_detail', kwargs={'slug': self.slug})
    
    def __str__(self) -> str:
        return self.name


class AccommodationType(models.Model):
    name = models.CharField(max_length=25, db_index=True)

    def __str__(self) -> str:
        return self.name


class FeaturedManager(models.Manager):
    def get_queryset(self):
        return super(FeaturedManager,self).get_queryset().filter(featured=True)

class Hotel(models.Model):
    name = models.CharField(max_length=25, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    destination = models.ForeignKey(
        Destination, related_name='hotels', on_delete=models.DO_NOTHING)
    intro = RichTextField()
    level = models.PositiveIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)])
    image = models.ImageField(upload_to='images/hotels', blank=True)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    objects = models.Manager()
    featuredHotels = FeaturedManager()

    def get_packages(self):
        return self.packages

    def __str__(self) -> str:
        return self.name


class HotelPackage(models.Model):
    hotel = models.ForeignKey(
        Hotel, related_name='packages', on_delete=models.RESTRICT)
    accommodation_type = models.ForeignKey(
        AccommodationType, on_delete=models.RESTRICT)
    label = models.CharField(max_length=50)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    single_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price, Half board'),
        blank=True, null=True,
    )
    single_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price, Full board'),
        blank=True, null=True,
    )
    double_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price, Half board'),
        blank=True, null=True,
    )
    double_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price, Full board'),
        blank=True, null=True,
    )
    triple_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price, Half board'),
        blank=True, null=True,
    )
    triple_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price, Full board'),
        blank=True, null=True,
    )
    
    @property
    def get_price_per_person_half(self):
        if self.double_room_half:
            return self.double_room_half / 2
        else:
            return 'Error , price not available'

    @property
    def get_price_per_person_full(self):
        if self.double_room_full:
            return self.double_room_full / 2
        else:
            return 'Error , price not available'

    def __str__(self) -> str:
        return self.label + " -- " + self.accommodation_type.name


class Booking(models.Model):
    # Personal info about client
    name = models.CharField(verbose_name=_('name'),
                            max_length=20,
                            blank=True,)
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=256,
        blank=True,
    )
    notes = models.TextField(
        max_length=1024,
        verbose_name=_('Notes'),
        blank=True,
    )
    # Booking info , attrs
    date_from = models.DateTimeField(
        verbose_name=_('From'),
        blank=True, null=True,
    )
    date_until = models.DateTimeField(
        verbose_name=_('Until'),
        blank=True, null=True,
    )
    time_period = models.PositiveIntegerField(
        verbose_name=_('Time period'),
        blank=True, null=True,
    )
    time_unit = models.CharField(
        verbose_name=_('Time unit'),
        default=getattr(settings, 'BOOKING_TIME_INTERVAL', ''),
        max_length=64,
        blank=True,
    )
    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
    )
    booking_id = models.CharField(
        max_length=100,
        verbose_name=_('Booking ID'),
        blank=True,
    )
    # Accommodation and transport
    accommodation = models.ForeignKey(
        Hotel, related_name='reservations', on_delete=models.RESTRICT)
    package = models.ForeignKey(
        HotelPackage, on_delete=models.RESTRICT, null=True, blank=True)
    adults = models.PositiveIntegerField(
        verbose_name=_('Number of Adults'),
        blank=True, null=True,
    )
    children = models.PositiveIntegerField(
        verbose_name=_('Number of Children'),
        blank=True, null=True,
    )
    transport = models.BooleanField(default=False)
    extra_seats = models.PositiveIntegerField(
        verbose_name=_('Number of extra seats'),
        blank=True, null=True,
    )
    total_seats = models.PositiveIntegerField(
        verbose_name=_('Number of total seats'),
        blank=True, null=True,
    )
    # payment
    booking_price = models.DecimalField(
        max_digits=36,
        decimal_places=2,
        verbose_name=_('Booking price'),
        blank=True, null=True,
    )
    transport_price = models.DecimalField(
        max_digits=36,
        decimal_places=2,
        verbose_name=_('Transport price'),
        blank=True, null=True,
    )
    total_price = models.DecimalField(
        max_digits=36,
        decimal_places=2,
        verbose_name=_('Total price'),
        blank=True, null=True,
    )

    paid_amount = models.DecimalField(
        max_digits=36,
        decimal_places=2,
        verbose_name=_('paid amount'),
        blank=True, null=True,
    )

    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return '#{} ({})'.format(self.booking_id or self.pk,
                                 self.creation_date)

    def calculate_remaining_amount(self):
        if self.total_price:
            return self.total_price - self.paid_amount
        else:
            return None


class BookingError(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        verbose_name=_('Booking'),
    )
    message = models.CharField(
        verbose_name=_('Message'),
        max_length=1000,
        blank=True,
    )
    details = models.TextField(
        verbose_name=_('Details'),
        max_length=4000,
        blank=True,
    )

    date = models.DateTimeField(
        verbose_name=_('Date'),
        auto_now_add=True,
    )

    def __str__(self):
        return u'[{0}] {1} - {2}'.format(self.date, self.booking.booking_id,
                                         self.message)


class Trip(models.Model):
    destination = models.ForeignKey(
        Destination, related_name='trips', on_delete=models.RESTRICT, verbose_name=_('destination'),)
    accommodation = models.ForeignKey(
        Hotel, related_name='trip_reservations', on_delete=models.RESTRICT, verbose_name=_('accommodation'),)
    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
    )
    creation_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='created_trips',
                                      on_delete=models.SET(get_sentinel_user),
                                      )

    date_from = models.DateField(
        verbose_name=_('From'),
    )
    date_until = models.DateField(
        verbose_name=_('Until'),
        
    )
    rooms_total = models.PositiveBigIntegerField(verbose_name=_('rooms total'),
                                               blank=True, null=True,)
    rooms_booked = models.PositiveBigIntegerField(verbose_name=_('rooms_booked'),
                                                  default=0)
    bus_total = models.PositiveBigIntegerField(verbose_name=_('bus_total'),
                                               blank=True, null=True,)
    meeting_location = models.CharField(verbose_name=_('Trip starting location'),
                                        max_length=256,
                                        blank=True,)
    transport_price_person = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Transport price per person'),
        default=0
    )


    single_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price / Person'),
        blank=True, null=True,
    )
    double_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price / Person'),
        blank=True, null=True,
    )
    triple_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price/ Person'),
        blank=True, null=True,
    )

    @property
    def get_price_per_person(self):
        if self.double_room_price:
            return self.double_room_price / 2
        else:
            return 'Error , price not available'

    @property
    def get_available_rooms(self):
        if self.rooms_total and self.rooms_booked:
            return(self.rooms_total - self.rooms_booked)
        else:
            return 'Error , price not available'

    @property
    def get_status(self):
        if self.date_from > date.today():
            return 'upcoming'
        if self.date_until < date.today():
            return 'previous'
        if self.date_from <= date.today() and self.date_until >= date.today():
            return 'ongoin'


    def __str__(self):
        return '#[{}] {} ({})'.format(self.id,self.accommodation.name,
                                 self.date_from)

    class Meta:
        ordering = ['-creation_date']
class TripBooking(models.Model):
    trip = models.ForeignKey(Trip, related_name='bookings',on_delete=models.CASCADE,verbose_name=_('Trip'))
    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
    )
    creation_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='created_trip_bookings',
                                      on_delete=models.SET(get_sentinel_user),
                                      )
    single_room_count = models.PositiveIntegerField(
        verbose_name=_('Single Rooms'),
        default=0,
    )
    double_room_count = models.PositiveIntegerField(
        verbose_name=_('Double Rooms'),
        default=0,
    )
    triple_room_count = models.PositiveIntegerField(
        verbose_name=_('Triple Rooms'),
        default=0,
    )
    single_room_persons = models.PositiveIntegerField(
        verbose_name=_('Persons in Single Rooms'),
        default=0,
    )
    double_room_persons = models.PositiveIntegerField(
        verbose_name=_('Persons in Double Rooms'),
        default=0,
    )
    triple_room_persons = models.PositiveIntegerField(
        verbose_name=_('Persons in Triple Rooms'),
        default=0,
    )
    adults = models.PositiveIntegerField(
        verbose_name=_('Adults'),
        default=0,
    )
    children = models.PositiveIntegerField(
        verbose_name=_('Children'),
        default=0,
    )
    extra_seats = models.PositiveIntegerField(
        verbose_name=_('Extra Seats'),
        default=0,
    )

    seats = models.TextField(null=True, blank=True)

    transport_price_person = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Transport price per person'),
        default=400,
    )

    discount_percentage = models.PositiveIntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(10)],
        default=0
        )

    discount_amount = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('discount amount'),
        default=0
    )
    discount_cause = models.TextField(
        null=True,blank=True
    )

    paid_amount = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Paid amount'),
        default=0
    )
    # Personal info about client
    name = models.CharField(verbose_name=_('Name'),
                            max_length=20,
                           )
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_('Phone number'),
        max_length=256,
    )
    phone2 = models.CharField(
        verbose_name=_('Additional Phone number'),
        max_length=256,
        blank=True,
    )
    notes = models.TextField(
        max_length=1024,
        verbose_name=_('Notes'),
        blank=True,
    )

    class Meta:
        ordering = ['-creation_date']
    def __str__(self) -> str:
        return f'[{self.get_rooms_count} Rooms] [{self.name}] [{self.phone}]'


    @property
    def get_rooms_count(self):
        return int(self.single_room_count)+int(self.double_room_count)+int(self.triple_room_count)

    @property
    def get_person_count(self):
        return(int(self.adults+self.children))

    @property
    def get_total_seats(self):
        return int(self.adults) + int(self.children) + int(self.extra_seats)
        
    @property
    def get_extra_seats_price(self):
        return self.extra_seats*self.trip.transport_price_person

    @property
    def get_primary_price(self):
        return Decimal(self.single_room_persons*self.trip.single_room_price+self.double_room_persons*self.trip.double_room_price+self.triple_room_persons*self.trip.triple_room_price)

    @property
    def get_discount(self):
        if self.discount_percentage > 0:
            return (self.discount_percentage / Decimal(100)) * self.get_primary_price
        return Decimal(0)

    @property
    def get_primary_price_after_discount(self):
        return int(self.get_primary_price - self.get_discount - self.discount_amount)

    @property
    def get_programs_price(self):
        return int(sum(x.get_price for x in self.programs.all()))

    @property
    def get_total_price(self):
        return(self.get_primary_price_after_discount+self.get_extra_seats_price+self.get_programs_price)

    @property
    def get_remained_price(self):
        return(self.get_total_price - self.paid_amount)

    @property
    def get_status(self):
        return('Active')

    
class TripProgram(models.Model):
    destination = models.ForeignKey(Destination,related_name='trip_programs',on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f'{self.name} [{self.price}] {self.destination.name}'
class TripBookingProgram(models.Model):
    booking = models.ForeignKey(TripBooking, related_name='programs',on_delete=models.CASCADE)
    program = models.ForeignKey(TripProgram, related_name='bookings', on_delete=models.SET('Deleted program'))
    quantity = models.PositiveIntegerField()

    @property
    def get_price(self):
        return int(self.quantity*self.program.price)

    def __str__(self) -> str:
        return f'[{self.booking.id}] [{self.program.name} X {self.quantity}] [{self.get_price}EGP]'

