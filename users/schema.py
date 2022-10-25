import graphene

from graphql_auth import mutations
from graphql_auth.schema import UserQuery, MeQuery


class AuthQuery(UserQuery, MeQuery, graphene.ObjectType):
    pass


class AuthMutation(graphene.ObjectType):
    register = mutations.Register.Field()
    verify_account = mutations.VerifyAccount.Field()
    token_auth = mutations.ObtainJSONWebToken.Field()
