import graphene

from bookings.schema import BookingQuery, BookingMutation
from users.schema import AuthQuery, AuthMutation


class Query(BookingQuery, AuthQuery):
    pass


class Mutation(BookingMutation, AuthMutation):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
