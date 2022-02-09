import * as Yup from 'yup';

let validationSchema = Yup.object().shape({
    // name: Yup.string()
    //     .min(5, 'Make the title longer than 5 characters.')
    //     .max(30, 'Make the title less than 30 characters.')
    //     .matches(/^[0-9a-z\_\-]+$/i, 'Remove any spaces or special characters.')
    //     .required(),

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
        .test(
            'Spearation or Orbital Period',
            'Separation and Orbital Period cannot be used together. Specify only one of them',
            (value) => !(value && orbitalPeriod.value)
        ),
    orbitalPeriod: Yup
        .number()
        .min(0.0)
        .test(
            'Spearation or Orbital Period',
            'Separation and Orbital Period cannot be used together. Specify only one of them',
            (value) => !(value && separation.value)
        ),
    velocityRandomNumber1: Yup
        .number()
        .min(0.0)
        .max(1.0),
    velocityRandomNumber2: Yup
        .number()
        .min(0.0)
        .max(1.0),
    velocity1: Yup
        .number()
        .min(0.0),
    velocity2: Yup
        .number()
        .min(0.0),
    theta1: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    theta2: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    phi1: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    phi2: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    meanAnomaly1: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    meanAnomaly2: Yup
        .number()
        .min(0.0)
        .max(2 * Math.PI),
    commonEnvelopeAlpha: Yup
        .number()
        .min(0.0),
    commonEnvelopeLambdaPrescription: Yup
        .string(),
    commonEnvelopeLambda: Yup
        .number()
        .min(0.0),
    remnantMassPrescription: Yup
        .string(),
    fryerSupernovaEngine: Yup
        .string(),
    blackHoleKicks: Yup
        .string(),
    kickVelocityDistribution: Yup
        .string(),
    kickVelocitySigmaCcsnNs: Yup
        .number()
        .min(0.0),
    kickVelocitySigmaCcsnBh: Yup
        .number()
        .min(0.0),
    kickVelocitySigmaEcsn: Yup
        .number()
        .min(0.0),
    kickVelocitySigmaUssn: Yup
        .number()
        .min(0.0),
    pairInstabilitySupernovae: Yup
        .boolean(),
    pisnLowerLimit: Yup
        .number()
        .min(0.0)
        .test(
            'pisnLowerLimit vs pisnUpperLimit',
            'PISN Upper Limit should be > PISN lower Limit',
            (value) => value < pisnUpperLimit.value
        ),
    pisnUpperLimit: Yup
        .number()
        .min(0.0)
        .test(
            'pisnUpperLimit vs pisnLowerLimit',
            'PISN Lower Limit should be < PISN Upper Limit',
            (value) => value > pisnLowerLimit.value
        ),
    pulsationalPairInstabilitySupernovae: Yup
        .boolean(),
    ppiLowerLimit: Yup
        .number()
        .min(0.0)
        .test(
            'ppiLowerLimit vs ppiUpperLimit',
            'PPI Upper Limit should be > PPI lower Limit',
            (value) => value < ppiUpperLimit.value
        ),
    ppiUpperLimit: Yup
        .number()
        .min(0.0)
        .test(
            'ppiUpperLimit vs ppiLowerLimit',
            'PPI Lower Limit should be < PPi Upper Limit',
            (value) => value > ppiLowerLimit.value
        ),
    pulsationalPairInstabilityPrescription: Yup
        .string(),
    maximumNeutronStarMass: Yup
        .number()
        .min(0.0),
    massTransferAngularMomentumLossPrescription: Yup
        .string(),
    massTransferAccertionEfficiencyPrescription: Yup
        .string(),
    massTransferFa: Yup
        .number()
        .min(0.0),
    massTransferJloss: Yup
        .number()
        .min(0.0),

}, [['mass1', 'mass2'], ['separation', 'orbitalPeriod'],
    ['pisnLowerLimit', 'pisnUpperLimit'], ['ppiLowerLimit', 'ppiUpperLimit']]);

export default validationSchema;
