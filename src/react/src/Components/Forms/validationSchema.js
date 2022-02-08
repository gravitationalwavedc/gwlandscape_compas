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
        .max(2 * Math.PI)
}, [['mass1', 'mass2'], ['separation', 'orbitalPeriod']]);

export default validationSchema;
