import * as Yup from 'yup';

let validationSchema = Yup.object().shape({
    mass1: Yup
        .number()
        .required()
        .min(0.0)
        .max(150.0)
        .test(
            'mass2 vs mass1',
            'Mass 1 should be > Mass 2',
            (value) => value > mass2.value
        ),
    mass2: Yup
        .number()
        .required()
        .min(0.1)
        .max(150.0)
        .test(
            'mass1 vs mass2',
            'Mass 2 should be < Mass 1',
            (value) => mass1.value > value
        ),
    metallicity: Yup
        .number()
        .required()
        .min(1e-4)
        .max(0.03),
    eccentricity: Yup
        .number()
        .required()
        .min(0.0)
        .max(1.0),
    separation: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable()
        .test(
            'Spearation or Orbital Period',
            'Separation and Orbital Period cannot be used together. Specify only one of them',
            (value) => !(value && orbitalPeriod.value)
        ),
    orbitalPeriod: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable()
        .test(
            'Spearation or Orbital Period',
            'Separation and Orbital Period cannot be used together. Specify only one of them',
            (value) => !(value && separation.value)
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
    commonEnvelopeAlpha: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable(),
    commonEnvelopeLambdaPrescription: Yup
        .string(),
    remnantMassPrescription: Yup
        .string(),
    fryerSupernovaEngine: Yup
        .string(),
    kickVelocityDistribution: Yup
        .string(),
    massTransferAngularMomentumLossPrescription: Yup
        .string(),
    massTransferAccretionEfficiencyPrescription: Yup
        .string(),
    massTransferFa: Yup
        .number()
        .min(0.0)
        .transform((value) => (isNaN(value) ? undefined : value))
        .nullable(),

}, [['mass1', 'mass2'], ['separation', 'orbitalPeriod']]);

export default validationSchema;
