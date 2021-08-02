import graphene
import compasui.schema


class Query(compasui.schema.Query, graphene.ObjectType):
    pass


class Mutation(compasui.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
