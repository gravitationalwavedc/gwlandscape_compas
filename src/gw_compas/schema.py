import graphene
import compasui.schema
import publications.schema
import adacs_sso_plugin.schema


class Query(
    compasui.schema.Query,
    publications.schema.Query,
    adacs_sso_plugin.schema.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    compasui.schema.Mutation,
    publications.schema.Mutation,
    adacs_sso_plugin.schema.Mutation,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
