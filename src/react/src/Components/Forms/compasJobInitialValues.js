const compasJobInitialValues = {
    name: 'Untitled',
    description: 'A good description is specific, unique, and memorable.',
    private: false,
    numberOfSystems: 10,
    minInitialMass: 5.0,
    maxInitialMass: 150.0,
    initialMassFunction: 'KROUPA',
    initialMassPower: 0.0,
    metallicityDistribution: 'ZSOLAR',
    minMetallicity: 0.0001,
    maxMetallicity: 0.03,
    minMassRatio: 0.01,
    maxMassRatio: 1.0,
    massRatioDistribution: 'FLAT',
    minSemiMajorAxis: 0.01,
    maxSemiMajorAxis: 1000.0,
    minOrbitalPeriod: 1.1,
    maxOrbitalPeriod: 1000.0,
    semiMajorAxisDistribution: 'FLATINLOG'
};

export default compasJobInitialValues;
