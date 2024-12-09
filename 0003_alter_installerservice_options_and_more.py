# Generated by Django 5.0.1 on 2024-11-09 14:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar_estimator', '0002_installationquote'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='installerservice',
            options={'verbose_name': 'Installation Service', 'verbose_name_plural': 'Installation Services'},
        ),
        migrations.AddField(
            model_name='installerservice',
            name='panel_size_range_max',
            field=models.FloatField(default=1.0, help_text='Maximum size of solar panels (in kW) for this service'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='installerservice',
            name='panel_size_range_min',
            field=models.FloatField(default=1, help_text='Minimum size of solar panels (in kW) for this service'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='installerservice',
            name='installer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='installation_services', to='solar_estimator.profile'),
        ),
        migrations.AlterField(
            model_name='installerservice',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Price for this installation service', max_digits=10),
        ),
        migrations.AlterField(
            model_name='installerservice',
            name='service_name',
            field=models.CharField(max_length=255),
        ),
        migrations.DeleteModel(
            name='InstallationQuote',
        ),
    ]
