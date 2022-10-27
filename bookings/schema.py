from uuid import uuid4

import graphene
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from bookings.models import Office, Booking


def is_user_authenticated(info):
    user = info.context.user
    if user.is_anonymous:
        raise Exception("not logged in")


class OfficeType(DjangoObjectType):
    class Meta:
        model = Office
        fields = ("uuid", "name")


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "squad", "club")


class BookingType(DjangoObjectType):
    class Meta:
        model = Booking
        interfaces = (Node,)
        fields = ("uuid", "office", "user", "date")
        filter_fields = ["user__squad", "date", "office_id"]


class BookingQuery(graphene.ObjectType):
    all_bookings = graphene.List(BookingType)
    all_offices = graphene.List(OfficeType)
    filter_bookings = DjangoFilterConnectionField(BookingType)

    @staticmethod
    def resolve_all_bookings(root, info):
        is_user_authenticated(info)
        return Booking.objects.all()

    @staticmethod
    def resolve_all_offices(root, info):
        is_user_authenticated(info)
        return Office.objects.all()

    @staticmethod
    def resolve_filter_bookings(root, info, *args, **kwargs):
        is_user_authenticated(info)
        return Booking.objects.all()


class BookingCreateMutation(graphene.Mutation):
    class Arguments:
        office_id = graphene.UUID(required=True)
        date = graphene.Date(required=True)

    booking = graphene.Field(BookingType)

    @classmethod
    def mutate(cls, root, info, office_id, date):
        is_user_authenticated(info)
        try:
            booking = Booking.objects.create(
                uuid=str(uuid4()),
                office_id=office_id,
                user=info.context.user,
                date=date,
            )
        except IntegrityError:
            raise GraphQLError("you can't book onto more than 1 office a day")
        return BookingCreateMutation(booking=booking)


class BookingUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)
        office_id = graphene.UUID(required=False)
        date = graphene.Date(required=False)

    booking = graphene.Field(BookingType)

    @classmethod
    def mutate(cls, root, info, uuid, office_id=None, date=None):
        is_user_authenticated(info)
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
        return BookingCreateMutation(booking=booking)


# TODO: I left this here as I wanted feedback on if using update_or_create was at all okay - I think I hate it, lol
# having it in a create and update class makes it much cleaner
class OfficeCreateOrUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID()
        name = graphene.String(required=True)

    office = graphene.Field(OfficeType)

    @classmethod
    def mutate(cls, root, info, name, uuid=uuid4()):
        is_user_authenticated(info)
        office, _ = Office.objects.update_or_create(
            uuid=str(uuid), defaults={"name": name}
        )
        return OfficeCreateOrUpdateMutation(office=office)


class OfficeDeleteMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    office = graphene.Field(OfficeType)

    @classmethod
    def mutate(cls, root, info, uuid):
        is_user_authenticated(info)
        # TODO: check what to respond here
        return Office.objects.filter(uuid=uuid).delete()


class BookingDeleteMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID(required=True)

    booking = graphene.Field(BookingType)

    @classmethod
    def mutate(cls, root, info, uuid):
        is_user_authenticated(info)
        # TODO: check what to respond here
        return Booking.objects.filter(uuid=uuid, user=info.context.user).delete()


class BookingMutation(graphene.ObjectType):

    create_booking = BookingCreateMutation.Field()
    update_booking = BookingUpdateMutation.Field()
    update_or_create_office = OfficeCreateOrUpdateMutation.Field()
    delete_office = OfficeDeleteMutation.Field()
    delete_booking = BookingDeleteMutation.Field()
