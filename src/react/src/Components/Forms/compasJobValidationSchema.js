import * as Yup from 'yup';

let validationSchema = Yup.object().shape({
  name: Yup.string()
    .min(5, 'Make the title longer than 5 characters.')
    .max(30, 'Make the title less than 30 characters.')
    .matches(/^[0-9a-z_-]+$/i, 'Remove any spaces or special characters.')
    .required(),
  numberOfSystems: Yup
    .number()
    .required()
    .min(1),
  initialMassPower: Yup
    .number()
    .nullable(),
  minInitialMass: Yup
    .number()
    .min(0.1)
    .nullable()
    .test(
      'Min Initial Mass vs Max Initial Mass',
      'Min Initial Mass should be < Max Initial Mass',
      (value, { parent }) => value < parent.maxInitialMass.value
    ),
  maxInitialMass: Yup
    .number()
    .max(150.0)
    .nullable()
    .test(
      'Min Initial Mass vs Max Initial Mass',
      'Min Initial Mass should be < Max Initial Mass',
      (value, { parent }) => value > parent.minInitialMass.value
    ),
  minMassRatio: Yup
    .number()
    .nullable()
    .test(
      'Min Mass Ratio vs Max Mass Ratio',
      'Min Mass Ratio should be > 0 and < Max Mass Ratio',
      (value, { parent }) => value > 0 && value < parent.maxMassRatio.value
    ),
  maxMassRatio: Yup
    .number()
    .nullable()
    .max(1.0)
    .test(
      'Min Mass Ratio vs Max Mass Ratio',
      'Min Mass Ratio should be < Max Mass Ratio',
      (value, { parent }) => value > parent.minMassRatio.value
    ),
  minSemiMajorAxis: Yup
    .number()
    .min(0.001)
    .nullable()
    .test(
      'Min Semi Major Axis vs Max Semi Major Axis',
      'Min Semi Major Axis should be < Max Semi Major Axis',
      (value, { parent }) => value < parent.maxSemiMajorAxis.value
    ),
  maxSemiMajorAxis: Yup
    .number()
    .nullable()
    .max(100000)
    .test(
      'Min Semi Major Axis vs Max Semi Major Axis',
      'Min Semi Major Axis should be < Max Semi Major Axis',
      (value, { parent }) => value > parent.minSemiMajorAxis.value
    ),
  minOrbitalPeriod: Yup
    .number()
    .min(1.0)
    .nullable()
    .test(
      'Min Orbital Period vs Max Orbital Period',
      'Min Orital Period should be < Max Orbital Period',
      (value, { parent }) => value < parent.maxOrbitalPeriod.value
    ),
  maxOrbitalPeriod: Yup
    .number()
    .nullable()
    .max(1000000)
    .test(
      'Min Orbital Period vs Max Orbital Period',
      'Min Orbital Period should be < Max Orbital Period',
      (value, { parent }) => value > parent.minOrbitalPeriod.value
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
  detailedOutput: Yup
    .bool()
    .required()

}, [['minInitialMass', 'maxInitialMass'],
['minMassRatio', 'maxMassRatio'],
['minSemiMajorAxis', 'maxSemiMajorAxis'],
['minOrbitalPeriod', 'maxOrbitalPeriod'],
]);

export default validationSchema;
