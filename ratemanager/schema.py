import graphene
import rate.schema
import account.schema
import countrycity.schema


class Query(rate.schema.Query, account.schema.Query, countrycity.schema.Query, graphene.ObjectType):
    pass


class Mutation(rate.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
