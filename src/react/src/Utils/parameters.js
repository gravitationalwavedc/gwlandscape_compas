const remnantMassPrescriptionOptions = [
    { value: 'HURLEY2000', label: 'HURLEY2000' },
    { value: 'BELCZYNSKI2002', label: 'BELCZYNSKI2002' },
    { value: 'FRYER2012', label: 'FRYER2012' },
    { value: 'MULLER2016', label: 'MULLER2016' },
    { value: 'MULLERMANDEL', label: 'MULLERMANDEL' },
];
const fryerSupernovaEngineOptions = [
    { value: 'DELAYED', label: 'DELAYED' },
    { value: 'RAPID', label: 'RAPID' },
];

const kickVelocityDistributionOptions = [
    { value: 'ZERO', label: 'ZERO' },
    { value: 'FIXED', label: 'FIXED' },
    { value: 'FLAT', label: 'FLAT' },
    { value: 'MAXWELLIAN', label: 'MAXWELLIAN' },
    { value: 'BRAYELDRIDGE', label: 'BRAYELDRIDGE' },
    { value: 'MULLER2016', label: 'MULLER2016' },
    { value: 'MULLER2016MAXWELLIAN', label: 'MULLER2016MAXWELLIAN' },
    { value: 'MULLERMANDEL', label: 'MULLERMANDEL' },
];

const massTransferAngularMomentumLossPrescriptionOptions = [
    { value: 'JEANS', label: 'JEANS' },
    { value: 'ISOTROPIC', label: 'ISOTROPIC' },
    { value: 'CIRCUMBINARY', label: 'CIRCUMBINARY' },
    { value: 'ARBITRARY', label: 'ARBITRARY' },
];

const massTransferAccretionEfficiencyPrescriptionOptions = [
    { value: 'THERMAL', label: 'THERMAL' },
    { value: 'FIXED', label: 'FIXED' },
];

const lambdaPrescriptionOptions = [
    { value: 'LAMBDA_FIXED', label: 'LAMBDA_FIXED' },
    { value: 'LAMBDA_LOVERIDGE', label: 'LAMBDA_LOVERIDGE' },
    { value: 'LAMBDA_NANJING', label: 'LAMBDA_NANJING' },
    { value: 'LAMBDA_KRUCKOW', label: 'LAMBDA_KRUCKOW' },
    { value: 'LAMBDA_DEWI', label: 'LAMBDA_DEWI' },
];

export {
    fryerSupernovaEngineOptions,
    remnantMassPrescriptionOptions,
    kickVelocityDistributionOptions,
    massTransferAngularMomentumLossPrescriptionOptions,
    massTransferAccretionEfficiencyPrescriptionOptions,
    lambdaPrescriptionOptions,
};
