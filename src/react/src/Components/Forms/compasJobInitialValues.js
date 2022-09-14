const compasJobInitialValues = {
    name: 'Untitled',
    description: 'A good description is specific, unique, and memorable.',
    private: true,
    numberOfSystems: 10,
    minInitialMass: 5.0,
    maxInitialMass: 150.0,
    initialMassFunction: 'KROUPA',
    metallicity: 0.0142,
    metallicityDistribution: 'ZSOLAR',
    minMetallicty: 0.0001,
    maxMetallicity: 0.03,
    minMassRatio: 0.01,
    maxMassRatio: 1.0,
    massRatioDistribution: 'FLAT',
    minSemiMajorAxis: 0.01,
    maxSemiMajorAxis: 1000.0,
    SemiMajorAxisDistribution: 'FLATINLOG'
};

export default compasJobInitialValues;
