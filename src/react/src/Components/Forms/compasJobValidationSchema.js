import * as Yup from 'yup';

let validationSchema = Yup.object().shape({
    numberOfSystems: Yup
        .number()
        .required()
        .min(1),
    intialMassPower: Yup
        .number()
        .nullable(),
    minInitialMass: Yup
        .number()
        .min(0.1)
        .nullable()
        .test(
            'Min Initial Mass vs Max Initial Mass',
            'Min Initial Mass should be < Max Initial Mass',
            (value) => value < maxInitialMass.value
        ),
    maxInitialMass: Yup
        .number()
        .max(150.0)
        .nullable()
        .test(
            'Min Initial Mass vs Max Initial Mass',
            'Min Initial Mass should be < Max Initial Mass',
            (value) => value > minInitialMass.value
        ),
    minMassRatio: Yup
        .number()
        .nullable()
        .test(
            'Min Mass Ratio vs Max Mass Ratio',
            'Min Mass Ratio should be > 0 and < Max Mass Ratio',
            (value) => value > 0 && value < maxMassRatio.value
        ),
    maxMassRatio: Yup
        .number()
        .nullable()
        .max(1.0)
        .test(
            'Min Mass Ratio vs Max Mass Ratio',
            'Min Mass Ratio should be < Max Mass Ratio',
            (value) => value > minMassRatio.value
        ),
    minSemiMajorAxis: Yup
        .number()
        .min(0.001)
        .nullable()
        .test(
            'Min Semi Major Axis vs Max Semi Major Axis',
            'Min Semi Major Axis should be < Max Semi Major Axis',
            (value) => value < maxSemiMajorAxis.value
        ),
    maxSemiMajorAxis: Yup
        .number()
        .nullable()
        .max(100000)
        .test(
            'Min Semi Major Axis vs Max Semi Major Axis',
            'Min Semi Major Axis should be < Max Semi Major Axis',
            (value) => value > minSemiMajorAxis.value
        ),
    minOrbitalPeriod: Yup
        .number()
        .min(1.0)
        .nullable()
        .test(
            'Min Orbital Period vs Max Orbital Period',
            'Min Orital Period should be < Max Orbital Period',
            (value) => value < maxOrbitalPeriod.value
        ),
    maxOrbitalPeriod: Yup
        .number()
        .nullable()
        .max(1000000)
        .test(
            'Min Orbital Period vs Max Orbital Period',
            'Min Orbital Period should be < Max Orbital Period',
            (value) => value > minOrbitalPeriod.value
        ),
    velocity1: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable(),
    velocity2: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable(),

}, [['minInitialMass', 'maxInitialMass'],
    ['minMassRatio', 'maxMassRatio'],
    ['minSemiMajorAxis', 'maxSemiMajorAxis'],
    ['minOrbitalPeriod', 'maxOrbitalPeriod'],
]);

export default validationSchema;