# Generated by Django 3.2.16 on 2022-10-25 12:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='booked',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='booked',
            unique_together={('user', 'date')},
        ),
    ]
