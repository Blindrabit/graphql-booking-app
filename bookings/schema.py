from uuid import uuid4

import graphene
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from bookings.models import Office, Booking


class OfficeType(DjangoObjectType):
    class Meta:
        model = Office
        fields = ("uuid", "name")


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email")


class BookingType(DjangoObjectType):
    class Meta:
        model = Booking
        interfaces = (Node,)
        fields = ("uuid", "office", "user", "date")
        filter_fields = ["user__squad", "date", "office"]


class BookingQuery(graphene.ObjectType):
    all_booked = graphene.List(BookingType)
    all_offices = graphene.List(OfficeType)
    all_bookings_by_squad = DjangoFilterConnectionField(BookingType)

    @staticmethod
    @login_required
    def resolve_all_booked(root, info):
        return Booking.objects.all()

    @staticmethod
    @login_required
    def resolve_all_offices(root, info):
        return Office.objects.all()


class BookingCreateMutation(graphene.Mutation):
    class Arguments:
        office_id = graphene.UUID(required=True)
        date = graphene.Date(required=True)

    booked = graphene.Field(BookingType)

    @classmethod
    @login_required
    def mutate(cls, root, info, office_id, date):
        try:
            booking = Booking.objects.create(
                uuid=str(uuid4()),
                office_id=office_id,
                user=info.context.user,
                date=date,
            )
        except IntegrityError:
            raise GraphQLError("you can't book onto more than 1 office a day")
        return BookingCreateMutation(booked=booking)


class BookingUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        office_id = graphene.UUID(required=False)
        date = graphene.Date(required=False)

    booked = graphene.Field(BookingType)

    @classmethod
    @login_required
    def mutate(cls, root, info, uuid, office_id=None, date=None):
        try:
            booking = Booking.objects.get(uuid=uuid, user=info.context.user)
        except Booking.DoesNotExist:
            raise GraphQLError("this booking does not exist")
        try:
            if office_id:
                booking.office_id = office_id
            if date:
                booking.date = date
            booking.save()
        except IntegrityError:
            raise GraphQLError("you can't book onto more than 1 office a day")
        return BookingCreateMutation(booked=booking)


# TODO: I left this here as I wanted feedback on if using update_or_create was at all okay - I think I hate it, lol
# having it in a create and update class makes it much cleaner
class OfficeCreateOrUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID()
        name = graphene.String(required=True)

    office = graphene.Field(OfficeType)

    @classmethod
    @login_required
    def mutate(cls, root, info, name, uuid=uuid4()):
        office, _ = Office.objects.update_or_create(
            uuid=str(uuid), defaults={"name": name}
        )
        return OfficeCreateOrUpdateMutation(office=office)


class OfficeDeleteMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    office = graphene.Field(OfficeType)

    @classmethod
    @login_required
    def mutate(cls, root, info, uuid):
        # TODO: check what to respond here
        return Office.objects.filter(uuid=uuid).delete()


class BookingDeleteMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    booking = graphene.Field(BookingType)

    @classmethod
    @login_required
    def mutate(cls, root, info, uuid):
        # TODO: check what to respond here
        return Booking.objects.filter(uuid=uuid, user=info.context.user).delete()


class BookingMutation(graphene.ObjectType):

    create_booking = BookingCreateMutation.Field()
    update_booking = BookingUpdateMutation.Field()
    update_or_create_office = OfficeCreateOrUpdateMutation.Field()
    delete_office = OfficeDeleteMutation.Field()
    delete_booking = BookingDeleteMutation.Field()
