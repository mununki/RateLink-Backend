import graphene
import graphql_jwt
import rate.schema
import account.schema
import countrycity.schema


class Query(rate.schema.Query, account.schema.Query, countrycity.schema.Query, graphene.ObjectType):
    pass


class Mutation(rate.schema.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
