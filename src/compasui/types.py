from graphene import AbstractType, ObjectType, Int, String, Boolean


class OutputStartType(ObjectType):
    name = String()
    description = String()
    private = Boolean()


class JobStatusType(ObjectType):
    name = String()
    number = Int()
    date = String()
