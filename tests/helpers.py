from datetime import date
from uuid import uuid4

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from graphql_jwt.testcases import JSONWebTokenTestCase

from bookings.models import Office, Booked


def create_office(name: str = "office"):
    return Office.objects.create(uuid=uuid4(), name=name)


def create_user(username: str = "user", email: str = "email@email.com", password: str = "super_secret_password123"):
    return get_user_model().objects.create(username=username, email=email, password=password)


def create_booking(user: settings.AUTH_USER_MODEL, office: Office, booking_date: date):
    return Booked.objects.create(uuid=uuid4(), user=user, office=office, date=booking_date)


class AuthenticatedClientTestCase(JSONWebTokenTestCase):
    @pytest.mark.django_db
    def setUp(self):
        self.user = create_user()
        self.client.authenticate(self.user)
