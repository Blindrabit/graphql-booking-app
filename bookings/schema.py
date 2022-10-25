from uuid import uuid4

import graphene
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from graphene import Node
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from graphql_jwt.decorators import login_required

from bookings.models import Office, Booked


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
        model = Booked
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
        return Booked.objects.all()

    @staticmethod
    @login_required
    def resolve_all_offices(root, info):
        return Office.objects.all()


class BookedCreateOrUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID()
        office_id = graphene.UUID(required=True)
        date = graphene.Date(required=True)

    booked = graphene.Field(BookingType)

    @classmethod
    @login_required
    def mutate(cls, root, info, office_id, date, uuid=uuid4()):
        try:
            booked, _ = Booked.objects.update_or_create(
                uuid=str(uuid), defaults={"office_id": office_id, "user_id": info.context.user.id, "date": date}
            )
        except IntegrityError:
            raise GraphQLError("you can't book onto more than 1 office a day")
        return BookedCreateOrUpdateMutation(booked=booked)


class OfficeCreateOrUpdateMutation(graphene.Mutation):
    class Arguments:
        uuid = graphene.UUID()
        name = graphene.String(required=True)

    office = graphene.Field(OfficeType)

    @classmethod
    @login_required
    def mutate(cls, root, info, name, uuid=uuid4()):
        office, _ = Office.objects.update_or_create(uuid=str(uuid), defaults={"name": name})
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
        return Booked.objects.filter(uuid=uuid, user=info.context.user).delete()


class BookingMutation(graphene.ObjectType):

    update_or_create_booking = BookedCreateOrUpdateMutation.Field()
    update_or_create_office = OfficeCreateOrUpdateMutation.Field()
    delete_office = OfficeDeleteMutation.Field()
    delete_booking = BookingDeleteMutation.Field()
