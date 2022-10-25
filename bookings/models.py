from django.conf import settings
from django.db import models


class Office(models.Model):
    uuid = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=128)


class Booked(models.Model):
    uuid = models.UUIDField(primary_key=True)
    office = models.ForeignKey("bookings.office", on_delete=models.CASCADE, related_name="booking")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="booking")
    date = models.DateField(null=True)

    class Meta:
        unique_together = ("user", "date")
