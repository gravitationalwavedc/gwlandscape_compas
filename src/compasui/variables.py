from types import SimpleNamespace

compas_parameters = SimpleNamespace()

compas_parameters.FAKE_DATA = ["simulated", "Simulated"]
compas_parameters.REAL_DATA = ["real", "Real"]

compas_parameters.DATA_SOURCES = [
    compas_parameters.FAKE_DATA,
    compas_parameters.REAL_DATA
]

compas_parameters.O1 = ["o1", "O1"]
compas_parameters.O2 = ["o2", "O2"]
compas_parameters.O3 = ["o3", "O3"]

compas_parameters.SOURCE_DATASETS = [
    compas_parameters.O1,
    compas_parameters.O2,
    compas_parameters.O3
]
