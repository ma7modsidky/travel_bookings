# Generated by Django 4.0.4 on 2022-04-28 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0019_alter_tripbooking_discount_amount_tripprogram_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tripbooking',
            name='paid_amount',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=36, verbose_name='Paid amount'),
        ),
        migrations.AlterField(
            model_name='tripbooking',
            name='transport_price_person',
            field=models.DecimalField(decimal_places=0, default=400, max_digits=36, verbose_name='Transport price per person'),
        ),
    ]
