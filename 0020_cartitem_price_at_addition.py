# Generated by Django 5.0.1 on 2024-11-26 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_estimator', '0019_profile_postcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='price_at_addition',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
