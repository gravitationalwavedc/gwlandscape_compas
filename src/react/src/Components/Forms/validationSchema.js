import * as Yup from 'yup';

let validationSchema = Yup.object().shape({
    name: Yup.string()
        .min(5, 'Make the title longer than 5 characters.')
        .max(30, 'Make the title less than 30 characters.')
        .matches(/^[0-9a-z\_\-]+$/i, 'Remove any spaces or special characters.')
        .required(),

    startFrequencyBand: Yup.number().required(),
    minStartTime: Yup.number().required(),
    maxStartTime: Yup.number().required(),

    asini: Yup.number().required(),
    freqBand: Yup.number().required(),
    alpha: Yup.number().required(),
    delta: Yup.number().required(),
    orbitTp: Yup.number().required(),
    orbitPeriod: Yup.number().required(),
    driftTime: Yup.number().required(),
    dFreq: Yup.number().required(),

    searchStartTime: Yup.number().required(),
    searchTBlock: Yup.number().required(),
    searchCentralA0: Yup.number().required(),
    searchA0Band: Yup.number().required(),
    searchA0Bins: Yup.number().required(),
    searchCentralP: Yup.number().required(),
    searchPBand: Yup.number().required(),
    searchPBins: Yup.number().required(),
    searchCentralOrbitTp: Yup.number().required(),
    searchOrbitTpBand: Yup.number().required(),
    searchOrbitTpBins: Yup.number().required(),
    searchLLThreshold: Yup.number().required()
});

export default validationSchema;
