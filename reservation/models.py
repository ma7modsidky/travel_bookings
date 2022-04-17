from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
# Create your models here.

class Destination(models.Model):
    name = models.CharField(max_length=25, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    intro = models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='images/destination', blank=True)
    # def get_absolute_url(self):
    #     return reverse('app:developer_detail', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.name

class AccommodationType(models.Model):
    name = models.CharField(max_length=25, db_index=True)

    def __str__(self) -> str:
        return self.name

class Hotel(models.Model):
    name = models.CharField(max_length=25, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    destination = models.ForeignKey(Destination, related_name='hotels', on_delete=models.DO_NOTHING)
    intro = models.TextField()
    level = models.PositiveBigIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(5)])
    image = models.ImageField(upload_to='images/hotels', blank=True)
    available = models.BooleanField(default=False)
    # price_per_night = models.DecimalField(
    #     max_digits=10, decimal_places=0, default=500000)


    # def get_absolute_url(self):
    #     return reverse('app:developer_detail', kwargs={'slug': self.slug})

    def get_packages(self):
        return self.packages
    def __str__(self) -> str:
        return self.name

class HotelPackage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='packages', on_delete=models.RESTRICT)
    accommodation_type = models.ForeignKey(AccommodationType, on_delete=models.RESTRICT)
    label = models.CharField(max_length=25)
    price_per_person_night_single = models.DecimalField(
        max_digits=10, decimal_places=0, default=1000)
    price_per_person_night_double = models.DecimalField(
        max_digits=10, decimal_places=0, default=1000)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

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
        verbose_name=('Notes'),
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
    package = models.ForeignKey(HotelPackage, on_delete=models.RESTRICT,null=True,blank=True)
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
