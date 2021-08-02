from graphene import AbstractType, ObjectType, Int, String, Boolean


class OutputStartType(ObjectType):
    name = String()
    description = String()
    private = Boolean()


class AbstractDataType(AbstractType):
    start_frequency_band = String()
    min_start_time = String()
    max_start_time = String()
    asini = String()
    freq_band = String()
    alpha = String()
    delta = String()
    orbit_tp = String()
    orbit_period = String()
    drift_time = String()
    d_freq = String()


class AbstractSearchType(AbstractType):
    search_start_time = String()
    search_t_block = String()
    search_central_a0 = String()
    search_a0_band = String()
    search_a0_bins = String()
    search_central_p = String()
    search_p_band = String()
    search_p_bins = String()
    search_central_orbit_tp = String()
    search_orbit_tp_band = String()
    search_orbit_tp_bins = String()
    search_l_l_threshold = String()


class JobStatusType(ObjectType):
    name = String()
    number = Int()
    date = String()
