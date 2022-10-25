from django.contrib.auth.models import AbstractUser
from django.db import models


class ExtendedUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=255, verbose_name="email")

    class Club(models.TextChoices):
        DEKKER = "dekker"

    club = models.CharField(max_length=128, choices=Club.choices, null=True)

    class Squad(models.TextChoices):
        LUNAR = "lunar"
        HORIZON = "horizon"
        POLARIS = " polaris"
        VOYAGER = "voyager"
        ORION = "orion"
        VANGUARD = "vanguard"
        PRACTICE_GROUP = "practice_group"

    squad = models.CharField(max_length=128, choices=Squad.choices, null=True)

    SQUAD_FIELD = "squad"
    CLUB_FIELD = "club"
