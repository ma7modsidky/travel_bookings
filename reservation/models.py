# import jsonfield
from decimal import Decimal
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta ,date
from django.template.defaultfilters import slugify

# Create your models here.
BOOKING_STATUS = (('active', 'ACTIVE'), ('cancelled', 'CANCELLED'))



def get_sentinel_user():
    return get_user_model().objects.get_or_create(username='deleted')[0]

class Client(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=50, db_index=True , unique=True)
    phone2 = models.CharField(max_length=50,blank=True,null=True)
    def __str__(self) -> str:
        return self.name
class Destination(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    intro = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/destination', blank=True)

    class Meta:
        ordering = ['name']
    def __str__(self) -> str:
        return self.name


class AccommodationType(models.Model):
    name = models.CharField(max_length=50, db_index=True)

    def __str__(self) -> str:
        return self.name


class FeaturedManager(models.Manager):
    def get_queryset(self):
        return super(FeaturedManager,self).get_queryset().filter(featured=True)


class GoingManager(models.Manager):
    def get_queryset(self):
        return super(GoingManager, self).bus_seats.objects.filter(seat_type='going')


class ReturnManager(models.Manager):
    def get_queryset(self):
        return super(ReturnManager, self).get_queryset().filter(seat_type='return')

class Hotel(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True )
    destination = models.ForeignKey(
        Destination, related_name='hotels', on_delete=models.DO_NOTHING)
    intro = RichTextField(blank=True)
    level = models.PositiveIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)])
    image = models.ImageField(upload_to='images/hotels', blank=True)
    available = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    objects = models.Manager()
    featuredHotels = FeaturedManager()

    class Meta:
        ordering = ['-level']
    def get_packages(self):
        return self.packages

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

class HotelPackage(models.Model):
    hotel = models.ForeignKey(
        Hotel, related_name='packages', on_delete=models.RESTRICT, verbose_name=_('Hotel'),)
    label = models.CharField(max_length=50, verbose_name=_('label'),)
    date_from = models.DateField(verbose_name=_('From'),)
    date_until = models.DateField(verbose_name=_('To'),)
    creation_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='created_packages',
                                      on_delete=models.SET(get_sentinel_user),
                                      null=True
                                      )
                                      
    single_room_half_available = models.BooleanField(default=False)
    single_room_full_available = models.BooleanField(default=False)
    double_room_half_available = models.BooleanField(default=False)
    double_room_full_available = models.BooleanField(default=False)
    triple_room_half_available = models.BooleanField(default=False)
    triple_room_full_available = models.BooleanField(default=False)


    single_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price, Half board'),
        default=0
    )

    single_room_half_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room cost, Half board'),
        default=0
    )
    single_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price, Full board'),
        default=0
    )
    single_room_full_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room cost, Full board'),
        default=0
    )
    double_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price, Half board'),
        default=0
    )
    double_room_half_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room cost, Half board'),
        default=0
    )
    double_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price, Full board'),
        default=0
    )
    double_room_full_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room cost, Full board'),
        default=0
    )
    triple_room_half = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price, Half board'),
        default=0
    )
    triple_room_half_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room cost, Half board'),
        default=0
    )
    triple_room_full = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price, Full board'),
        default=0
    )
    triple_room_full_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room cost, Full board'),
        default=0
    )
    
    # @property
    # def get_price_per_person_half(self):
    #     if self.double_room_half:
    #         return self.double_room_half / 2
    #     else:
    #         return 'Error , price not available'

    # @property
    # def get_price_per_person_full(self):
    #     if self.double_room_full:
    #         return self.double_room_full / 2
    #     else:
    #         return 'Error , price not available'
    @property
    def get_status(self):
        if self.date_from <= date.today() and self.date_until >= date.today():
            return True
        else:
            return False

    
    def __str__(self) -> str:
        return self.label


class Booking(models.Model):
    # Personal info about client
    client = models.ForeignKey(
        Client, related_name='ibookings', on_delete=models.SET_NULL, null=True)
    name = models.CharField(verbose_name=_('name'),
                            max_length=100,
                            )
    email = models.EmailField(
        verbose_name=_('Email'),
        blank=True,
    )
    phone = models.CharField(
        verbose_name=_('Phone'),
        max_length=256,
    )
    notes = models.TextField(
        max_length=1024,
        verbose_name=_('Notes'),
        blank=True,
    )
    # Booking info , attrs
    date_from = models.DateField(
        verbose_name=_('From'),
    )
    date_until = models.DateField(
        verbose_name=_('Until'),
    )
    time_period = models.PositiveIntegerField(
        verbose_name=_('Time period'),
        blank=True, null=True,
    )
    time_unit = models.CharField(
        verbose_name=_('Time unit'),
        default=getattr(settings, 'BOOKING_TIME_INTERVAL', ''),
        max_length=64,
        blank=True, null=True,
    )
    creation_date = models.DateTimeField(
        verbose_name=_('Creation date'),
        auto_now_add=True,
    )
    creation_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='created_bookings',
                                      on_delete=models.SET(get_sentinel_user),
                                      )
    
    # Accommodation and transport
    accommodation = models.ForeignKey(
        Hotel, related_name='reservations', on_delete=models.RESTRICT)
    accommodation_type = models.ForeignKey(
        AccommodationType, on_delete=models.RESTRICT, default=1, verbose_name=_('Accommodation type'))
    package = models.ForeignKey(
        HotelPackage, on_delete=models.RESTRICT)
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
    adults = models.PositiveIntegerField(
        verbose_name=_('Number of Adults'),
        default=0,
    )
    children = models.PositiveIntegerField(
        verbose_name=_('Number of Children'),
        default=0,
    )
    transport = models.BooleanField(
        default=False, verbose_name=_('Transport'),)
    seats_booked = models.BooleanField(default=False)
    transport_price_person = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Transport price per person'),
        default=400,
    )
    extra_seats = models.PositiveIntegerField(
        verbose_name=_('Number of extra seats'),
        default=0,
    )
    # payment
    discount_percentage = models.PositiveIntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(10)],
        default=0,
        verbose_name=_('discount percentage'),
    )

    discount_amount = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('discount amount'),
        default=0
    )
    paid_amount = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('paid amount'),
        default=0
    )

    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default=BOOKING_STATUS[0][0])
    
    class Meta:
        ordering = ['-creation_date']
    # def clean(self):
    
    #     if self.date_from > self.package.date_until or self.date_until > self.package.date_until:
    #         raise ValidationError(_('Booking not in the right dates of the package'))
       

    def __str__(self):
        return '#{} ({})'.format(self.id,
                                 self.creation_date)

    @property
    def get_nights_count(self):
        delta = (self.date_until - self.date_from)
        return int(delta.days)

    @property
    def get_rooms_count(self):
        return int(self.single_room_count)+int(self.double_room_count)+int(self.triple_room_count)

    @property
    def get_description(self):
        single = _('Single rooms')
        double = _('Double rooms')
        triple = _('Triple rooms')
        description = ''
        if self.single_room_count > 0:
            description += f'[{self.single_room_count}] {single} \n'
        if self.double_room_count > 0:
            description += f'[{self.double_room_count}] {double} \n'
        if self.triple_room_count > 0:
            description += f'[{self.triple_room_count}] {triple} \n'
        return description

    @property
    def get_person_count(self):
        return(int(self.adults+self.children))

    @property
    def get_total_seats(self):
        return int(self.adults) + int(self.children) + int(self.extra_seats)

    @property
    def get_extra_seats_price(self):
        return self.extra_seats*self.transport_price_person

    @property
    def get_halfboard_price(self):
        return Decimal(self.single_room_count*self.package.single_room_half+self.double_room_count*self.package.double_room_half+self.triple_room_count*self.package.triple_room_half)

    @property
    def get_halfboard_cost(self):
        return Decimal(self.single_room_count*self.package.single_room_half_cost+self.double_room_count*self.package.double_room_half_cost+self.triple_room_count*self.package.triple_room_half_cost)

    @property
    def get_fullboard_price(self):
        return Decimal((self.single_room_count*self.package.single_room_full)+(self.double_room_count*self.package.double_room_full)+(self.triple_room_count*self.package.triple_room_full))

    @property
    def get_fullboard_cost(self):
        return Decimal(self.single_room_count*self.package.single_room_full_cost+self.double_room_count*self.package.double_room_full_cost+self.triple_room_count*self.package.triple_room_full_cost)


    @property
    def get_primary_price(self):
        if self.accommodation_type.name == 'Half Board':
            return self.get_halfboard_price*self.get_nights_count
        elif self.accommodation_type.name == 'Full Board':
            return self.get_fullboard_price*self.get_nights_count

    @property
    def get_primary_cost(self):
        if self.accommodation_type.name == 'Half Board':
            return self.get_halfboard_cost*self.get_nights_count
        elif self.accommodation_type.name == 'Full Board':
            return self.get_fullboard_cost*self.get_nights_count


    @property
    def get_discount(self):
        if self.discount_percentage > 0:
            return (self.discount_percentage / Decimal(100)) * self.get_primary_price
        return int(0)

    @property
    def get_primary_price_after_discount(self):
        return int(self.get_primary_price - self.get_discount - self.discount_amount)

    @property
    def get_primary_price_after_discount_2(self):
        return int(self.get_primary_price - self.get_discount)

    @property
    def get_profit(self):
        return self.get_primary_price_after_discount-self.get_primary_cost

    @property
    def get_total_price(self):
        return self.get_primary_price_after_discount

    @property
    def get_remained_price(self):
        return(self.get_total_price - self.paid_amount)

    @property
    def get_status(self):
        if self.date_from > date.today():
            return 'upcoming'
        if self.date_until < date.today():
            return 'previous'
        if self.date_from <= date.today() and self.date_until >= date.today():
            return 'ongoing'

    @property
    def get_active_status(self):
        
        if self.status == BOOKING_STATUS[0][0]:
            return 'active'
        elif self.status == BOOKING_STATUS[1][0]:
            return 'cancelled'
        else:
            return None

    @property
    def get_cancellation_price(self):
        if self.status == 'cancelled':
            return self.get_primary_price_after_discount // 2
        else:
            return self.get_primary_price_after_discount // 2
    @property
    def get_payment_status(self):
        if self.get_remained_price > 0 :
            return 'remaining'
        else :
            return 'complete'

    @property
    def get_single_room_price(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.single_room_half
        elif self.accommodation_type.name == 'Full Board':
            return self.package.single_room_full

    @property
    def get_single_room_price_all(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.single_room_half* self.single_room_count
        elif self.accommodation_type.name == 'Full Board':
            return self.package.single_room_full * self.single_room_count

    @property
    def get_double_room_price(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.double_room_half
        elif self.accommodation_type.name == 'Full Board':
            return self.package.double_room_full 

    @property
    def get_double_room_price_all(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.double_room_half* self.double_room_count
        elif self.accommodation_type.name == 'Full Board':
            return self.package.double_room_full * self.double_room_count

    @property
    def get_triple_room_price(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.triple_room_half
        elif self.accommodation_type.name == 'Full Board':
            return self.package.triple_room_full

    @property
    def get_triple_room_price_all(self):
        if self.accommodation_type.name == 'Half Board':
            return self.package.triple_room_half *self.triple_room_count
        elif self.accommodation_type.name == 'Full Board':
            return self.package.triple_room_full * self.triple_room_count

    @property
    def get_price_per_night(self):
        return self.get_triple_room_price_all+self.get_double_room_price_all+self.get_single_room_price_all

    @property
    def get_seats_num(self):
        return list(self.bus_seats.values_list('number', flat=True).distinct())
    
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
    meeting_time = models.CharField(verbose_name=_('Trip starting time'),
                                        max_length=256,
                                        blank=True,)
    transport_price_person = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Transport price per person'),
        default=0
    )
    single_room_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('single room cost'),
    )
    double_room_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('double room cost'),
    )
    triple_room_cost = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('triple room cost'),
    )

    single_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Single Room price / Person'),
    )
    
    double_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Double Room price / Person'),
    )
    triple_room_price = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Triple Room price/ Person'),
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

    @property
    def get_nights_count(self):
        delta = (self.date_until - self.date_from)
        return int(delta.days)

    def __str__(self):
        return '[{}] {} ({})'.format(self.id,self.accommodation.name,
                                 self.date_from)

    class Meta:
        ordering = ['-date_from']
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

    seats_booked = models.BooleanField(default=False)

    discount_percentage = models.PositiveIntegerField(validators=[
        MinValueValidator(0),
        MaxValueValidator(10)],
        default=0,
        verbose_name=_('discount percentage'),
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
                            max_length=50,
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
    client = models.ForeignKey(Client, related_name='trip_bookings', on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20, choices=BOOKING_STATUS, default=BOOKING_STATUS[0][0])
       
    class Meta:
        ordering = ['-creation_date']
    def __str__(self) -> str:
        return f'[{self.get_rooms_count} Rooms] [{self.name}] [{self.phone}]'

    @property
    def get_seats_num(self):
        return list(self.bus_seats.values_list('number', flat=True).distinct())

    @property
    def get_nights_count(self):
        delta = (self.trip.date_until - self.trip.date_from)
        return int(delta.days)
    
    @property
    def get_description(self):
        single = _('Single rooms')
        double = _('Double rooms')
        triple = _('Triple rooms')
        description = ''
        if self.single_room_count > 0:
            description += f'[{self.single_room_count}] {single} \n'
        if self.double_room_count > 0:
            description += f'[{self.double_room_count}] {double} \n'
        if self.triple_room_count > 0:
            description += f'[{self.triple_room_count}] {triple} \n'
        return description

    @property
    def get_single_rooms_cost_night(self):
        return self.single_room_count*self.trip.single_room_cost

    @property
    def get_double_rooms_cost_night(self):
        return self.double_room_count*self.trip.double_room_cost

    @property
    def get_triple_rooms_cost_night(self):
        return self.triple_room_count*self.trip.triple_room_cost

    @property
    def get_all_rooms_cost_night(self):
        return self.get_single_rooms_cost_night + self.get_double_rooms_cost_night + self.get_triple_rooms_cost_night
    
    @property
    def get_all_cost(self):
        return self.get_all_rooms_cost_night * self.get_nights_count

    @property
    def get_all_programs_cost(self):
        try:
            return int(sum(x.get_cost for x in self.programs.all()))
        except:
            return 0
    
    @property
    def get_final_cost(self):
        return self.get_all_cost + self.get_all_programs_cost

    @property
    def get_profit(self):
        return self.get_total_price-self.get_final_cost

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
    def get_single_price(self):
        return self.single_room_persons*self.trip.single_room_price

    @property
    def get_double_price(self):
        return self.double_room_persons*self.trip.double_room_price

    @property
    def get_triple_price(self):
        return self.triple_room_persons*self.trip.triple_room_price

    @property
    def get_primary_price(self):
        return Decimal(self.single_room_persons*self.trip.single_room_price+self.double_room_persons*self.trip.double_room_price+self.triple_room_persons*self.trip.triple_room_price)

    @property
    def get_primary_price2(self):
        return self.get_single_price+self.get_double_price+self.get_triple_price
    @property
    def get_discount(self):
        if self.discount_percentage > 0:
            return (self.discount_percentage / Decimal(100)) * self.get_primary_price
        return Decimal(0)

    @property
    def get_primary_price_after_discount_percentage(self):
        return int(self.get_primary_price - self.get_discount)

    @property
    def get_primary_price_after_discount(self):
        return int(self.get_primary_price - self.get_discount - self.discount_amount)

    @property
    def get_price_with_extra_seats(self):
        return self.get_primary_price_after_discount + self.get_extra_seats_price

    @property
    def get_price_with_extra_amount(self):
        return self.get_price_with_extra_seats + self.get_amounts_price

    @property
    def get_programs_price(self):
        try:
            return int(sum(x.get_price for x in self.programs.all()))
        except:
            return 0
    @property
    def get_amounts_price(self):
        return int(sum(x.price for x in self.additional_amounts.all()))

    @property
    def get_total_price(self):
        return(self.get_primary_price_after_discount+self.get_extra_seats_price+self.get_programs_price+self.get_amounts_price)

    @property
    def get_remained_price(self):
        return(self.get_total_price - self.paid_amount)

    @property
    def get_status(self):
        
        if self.status == BOOKING_STATUS[0][0]:
            return 'active'
        elif self.status == BOOKING_STATUS[1][0]:
            return 'cancelled'
        else:
            return None    


    @property
    def get_cancellation_price(self):
        if self.status == 'cancelled':
            return self.get_primary_price_after_discount // 2
        else:
            return self.get_primary_price_after_discount // 2

    @property
    def get_payment_status(self):
        if self.get_remained_price > 0:
            return 'remaining'
        else:
            return 'complete'
    
class TripProgram(models.Model):
    destination = models.ForeignKey(Destination,related_name='trip_programs',on_delete=models.CASCADE)
    name = models.CharField(max_length=100 , verbose_name='name')
    cost = models.PositiveIntegerField(verbose_name='cost')
    price = models.PositiveIntegerField(verbose_name='price')

    def __str__(self) -> str:
        return f'{self.name} [{self.price}] {self.destination.name}'
class TripBookingProgram(models.Model):
    booking = models.ForeignKey(TripBooking, related_name='programs',on_delete=models.CASCADE)
    program = models.ForeignKey(TripProgram, related_name='bookings', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.PositiveIntegerField()
    unit_cost = models.PositiveIntegerField()
    unit_name = models.CharField(max_length=100)

    @property
    def get_price(self):
        try:
            return int(self.quantity*self.unit_price)
        except:
            return 0

    @property
    def get_cost(self):
        try:
            return int(self.quantity*self.unit_cost)
        except:
            return 0

    @property
    def get_profit(self):
        try:
            return self.get_price - self.get_cost
        except:
            return 0

    def __str__(self) -> str:
        return f'[{self.booking.id}] [{self.unit_name} X {self.quantity}] [{self.get_price}EGP]'

class AdditionalAmount(models.Model):
    price = models.PositiveIntegerField(verbose_name='price')
    reason = models.CharField(max_length=150)
    booking = models.ForeignKey(TripBooking, related_name='additional_amounts',on_delete=models.CASCADE,null=True,blank=True)
    ibooking = models.ForeignKey(Booking, related_name='additional_amounts',on_delete=models.CASCADE,null=True,blank=True)


PAYMENT_TYPE = (('tripbooking', 'TRIPBOOKING'), ('ibooking', 'IBOOKING'))
class PaymentRecord(models.Model):
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE)
    amount = models.PositiveIntegerField(verbose_name='amount')
    booking = models.ForeignKey(TripBooking,related_name='payment_records', on_delete=models.CASCADE,null=True,blank=True)
    ibooking = models.ForeignKey(Booking,related_name='payment_records', on_delete=models.CASCADE,null=True,blank=True)
    creation_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      related_name='payment_records',
                                      on_delete=models.SET(get_sentinel_user),
                                      )
    creation_date = models.DateTimeField(
        verbose_name=_('date'),
        auto_now_add=True,
    )

    def __str__(self) -> str:
        return f'{self.amount} EGP for {self.payment_type}'