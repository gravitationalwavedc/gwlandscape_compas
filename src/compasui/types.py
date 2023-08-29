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
    initial_mass_power = String()
    min_metallicity = String()
    max_metallicity = String()
    metallicity_distribution = String()
    min_mass_ratio = String()
    max_mass_ratio = String()
    mass_ratio_distribution = String()
    min_semi_major_axis = String()
    max_semi_major_axis = String()
    semi_major_axis_distribution = String()
    min_orbital_period = String()
    max_orbital_period = String()
    detailed_output = String()


class AbstractAdvancedParametersType(AbstractType):
    mass_transfer_angular_momentum_loss_prescription = String()
    mass_transfer_accretion_efficiency_prescription = String()
    mass_transfer_fa = String()
    common_envelope_alpha = String()
    common_envelope_lambda_prescription = String()
    remnant_mass_prescription = String()
    fryer_supernova_engine = String()
    kick_velocity_distribution = String()
    velocity_1 = String()
    velocity_2 = String()
