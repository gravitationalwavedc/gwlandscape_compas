from graphene import AbstractType, ObjectType, Int, String, Boolean


class OutputStartType(ObjectType):
    name = String()
    description = String()
    private = Boolean()


class JobStatusType(ObjectType):
    name = String()
    number = Int()
    date = String()


class AbstractBasicParameterType(AbstractType):
    number_of_systems = String()
    min_initial_mass = String()
    max_initial_mass = String()
    initial_mass_function = String()
    metallicity = String()
    min_metallicity = String()
    max_metallicity = String()
    metallicity_distribution = String()
    min_mass_ratio = String()
    max_mass_ratio = String()
    mass_ratio_distribution = String()
    min_semi_major_axis = String()
    max_semi_major_axis = String()
    semi_major_axis_distribution = String()
