const initialValues = {
    mass1: 35.0,
    mass2: 31.0,
    metallicity: 0.001,
    eccentricity: 0.0,
    separation: 3.5,
    orbitalPeriod: '',
    velocity1: 0.0,
    velocity2: 0.0,
    commonEnvelopeAlpha: 1.0,
    commonEnvelopeLambdaPrescription: 'LAMBDA_NANJING',
    // commonEnvelopeLambda: 0.1,
    remnantMassPrescription: 'FRYER2012',
    fryerSupernovaEngine: 'DELAYED',
    blackHoleKicks: 'FALLBACK',
    kickVelocityDistribution: 'MAXWELLIAN',
    massTransferAngularMomentumLossPrescription: 'ISOTROPIC',
    massTransferAccretionEfficiencyPrescription: 'THERMAL',
    massTransferFa: 0.5,
    // massTransferJloss: 0.1,
};

export default initialValues;
