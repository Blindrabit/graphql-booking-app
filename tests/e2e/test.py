import arrow
import datetime

from bookings.models import Office, Booked
from tests import helpers


class TestOfficeEndPoints(helpers.AuthenticatedClientTestCase):
    def test_query_all_offices(self):
        office = helpers.create_office()
        response = self.client.execute("query allOffices{allOffices{uuid name}}")
        data = response.data.get("allOffices")
        assert len(data) == 1
        assert data[0].get("uuid") == str(office.uuid)
        assert data[0].get("name") == office.name

    def test_create_office(self):
        response = self.client.execute(
            'mutation createOffice{ updateOrCreateOffice (name: "office"){ office{ uuid name}}}',
        )
        response_office = response.data.get("updateOrCreateOffice").get("office")
        office = Office.objects.get(uuid=response_office.get("uuid"))
        assert office.name == response_office.get("name")

    def test_update_office(self):
        office = helpers.create_office()
        office_uuid = str(office.uuid)
        response = self.client.execute(
            """
            mutation updateOffice { 
                updateOrCreateOffice (name: "new office", uuid: "%s") { 
                    office { 
                        uuid 
                        name
                    }
                }
            }
            """
            % office_uuid
        )
        office = Office.objects.get(uuid=office_uuid)
        assert office.name == "new office"

    def test_delete_office(self):
        office = helpers.create_office()
        office_uuid = str(office.uuid)
        response = self.client.execute(
            'mutation deleteOffice { deleteOffice (uuid: "%s"){ office {uuid}}}'
            % office_uuid
        )
        assert not Office.objects.filter(uuid=office_uuid)


class TestBookingEndPoints(helpers.AuthenticatedClientTestCase):
    def test_query_all_bookings(self):
        office = helpers.create_office()
        booking = helpers.create_booking(
            user=self.user, office=office, booking_date=datetime.date.today()
        )
        response = self.client.execute(
            "query allBooked{ allBooked{ uuid office{ uuid name} user{ id username} date}}"
        )
        data = response.data.get("allBooked")
        assert len(data) == 1
        assert data[0].get("uuid") == str(booking.uuid)
        assert data[0].get("date") == str(booking.date)

        assert data[0].get("office").get("uuid") == str(office.uuid)
        assert data[0].get("office").get("name") == office.name

        assert data[0].get("user").get("id") == str(self.user.id)
        assert data[0].get("user").get("username") == self.user.username

    def test_create_booking(self):
        office = helpers.create_office()
        response = self.client.execute(
            """
            mutation updateOrCreateBooking {
                updateOrCreateBooking (officeId: "%s", date: "%s"){
                    booked {
                        date
                        office {
                            uuid
                        }
                        user {
                            id
                        }
                    }
                }
            }
            """
            % (str(office.uuid), arrow.utcnow().date().isoformat())
        )
        booking = Booked.objects.all()
        assert booking.count() == 1
        booking = booking.first()
        assert booking.date == datetime.date.today()
        assert booking.user == self.user
        assert booking.office == office

    def test_update_booking_date(self):
        office = helpers.create_office()
        today_date = arrow.utcnow()
        booking = helpers.create_booking(
            user=self.user, office=office, booking_date=today_date.date()
        )
        response = self.client.execute(
            """
            mutation updateOrCreateBooking {
                updateOrCreateBooking (uuid: "%s", officeId: "%s", date: "%s"){
                    booked {
                        uuid
                        date
                    }
                }
            }
            """
            % (
                str(booking.uuid),
                str(office.uuid),
                today_date.shift(days=1).date().isoformat(),
            )
        )
        booking = Booked.objects.get(uuid=booking.uuid)
        assert booking.date == today_date.shift(days=1).date()

        assert booking.office == office
        assert booking.user == self.user

    def test_update_booking_office(self):
        office_1 = helpers.create_office()
        office_2 = helpers.create_office(name="office 2")
        today_date = arrow.utcnow()
        booking = helpers.create_booking(
            user=self.user, office=office_1, booking_date=today_date.date()
        )
        response = self.client.execute(
            """
            mutation updateOrCreateBooking {
                updateOrCreateBooking (uuid: "%s", officeId: "%s", date: "%s"){
                    booked {
                        uuid
                        date
                    }
                }
            }
            """
            % (str(booking.uuid), str(office_2.uuid), today_date.date().isoformat())
        )
        booking = Booked.objects.get(uuid=booking.uuid)
        assert booking.office == office_2

        assert booking.date == today_date.date()
        assert booking.user == self.user

    def test_user_booked_into_multiple_offices_on_same_date_fails(self):
        office_1 = helpers.create_office()
        office_2 = helpers.create_office(name="office 2")
        today_date = arrow.utcnow()
        booking = helpers.create_booking(
            user=self.user, office=office_1, booking_date=today_date.date()
        )
        response = self.client.execute(
            """
            mutation updateOrCreateBooking {
                updateOrCreateBooking (officeId: "%s", date: "%s"){
                    booked {
                        date
                        office {
                            uuid
                        }
                        user {
                            id
                        }
                    }
                }
            }
            """
            % (str(office_2.uuid), arrow.utcnow().date().isoformat())
        )
        assert str(response.errors[0]) == "you can't book onto more than 1 office a day"

    def test_delete_booking(self):
        office_1 = helpers.create_office()
        today_date = arrow.utcnow()
        booking = helpers.create_booking(
            user=self.user, office=office_1, booking_date=today_date.date()
        )
        booking_uuid = booking.uuid
        response = self.client.execute(
            'mutation deleteBooking{ deleteBooking (uuid: "%s"){ booking {uuid}}}'
            % str(booking_uuid)
        )
        assert not Booked.objects.filter(uuid=booking_uuid)
