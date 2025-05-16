import graphene
import compasui.schema
import publications.schema


class Query(compasui.schema.Query, publications.schema.Query, graphene.ObjectType):
    pass


class Mutation(
    compasui.schema.Mutation, publications.schema.Mutation, graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
