import React from 'react';

const units = {
    time: 'Myr',
    Temperature: 'K',
    Luminosity: <>L<sub>&#8857;</sub></>,
    mass: <>M<sub>&#8857;</sub></>,
    _length: <>R<sub>&#8857;</sub></>
};

const mass = (data) => ({
    totalMass1: data['Mass(1)'],
    totalMass2: data['Mass(2)'],
    mass_ZAMS1: data['Mass@ZAMS(1)'],
    mass_ZAMS2: data['Mass@ZAMS(2)'],
    mass_0_1: data['Mass_0(1)'],
    mass_0_2: data['Mass_0(2)'],
    mass_CO_core1: data['Mass_CO_Core(1)'],
    mass_CO_core2: data['Mass_CO_Core(2)'],
    mass_core_1: data['Mass_Core(1)'],
    mass_core_2: data['Mass_Core(2)'],
    mass_HE_core1: data['Mass_He_Core(1)'],
    mass_HE_core2: data['Mass_He_Core(2)'],
    mass_env1: data['Mass_Env(1)'],
    mass_env2: data['Mass_Env(2)'],
    time: data['Time'],
    systemMass: data['Mass(1)'].map((m, i) => m + data['Mass(2)'][i]),
});

const length = (data) => ({
    semimajor: data['SemiMajorAxis'],
    eccentricity: data['Eccentricity'],
    radius_1: data['Radius(1)'],
    radius_2: data['Radius(2)'],
    roche_radius_1: data['RocheLobe(1)'],
    roche_radius_2: data['RocheLobe(2)'],
    time: data['Time'],
    periapsis: data['SemiMajorAxis'].map((sma, i) => sma * (1 - data['Eccentricity'][i]))
});

const hrattr = (data) => {
    if (!data) {
        return ({});
    }

    return ({
        teff_1: data['Teff(1)'],
        teff_2: data['Teff(2)'],
        luminosity_1: data['Luminosity(1)'],
        luminosity_2: data['Luminosity(2)'],
        time: data['Time']
    });
};

const vdhattr = (data) => ({
    time: data['Time'],
    semimajor: data['SemiMajorAxis'],
    mass1: data['Mass(1)'],
    mass2: data['Mass(2)'],
    eccentricity: data['Eccentricity'],
    MT_history: data['MT_History'],
    Stellar_Type1: data['Stellar_Type(1)'],
    Stellar_Type2: data['Stellar_Type(2)'],
    Z1: data['Metallicity@ZAMS(1)']
});

const getMinMax = (data, xKey, yKeys) => {
    let yData = [];
    Object.keys(yKeys).forEach((key) => {
        yData = yData.concat(data[key]);
    });
    return [[data[xKey][0], data[xKey].at(-1)], [Math.min(...yData), Math.max(...yData)]];
};

const compareDomains = (d1, d2) => d1.x1 === d2.x1 &&
    d1.x2 === d2.x2 &&
    d1.y1 === d2.y1 &&
    d1.y2 === d2.y2;

const mapLineData = (dataset, keys = null) => {
    let data = [];
    dataset.time.forEach((_, i) => {
        let obj = {};
        let objkeys = keys ? Object.keys(keys) : Object.keys(dataset);
        objkeys.forEach(key => { keys ? obj[keys[key]] = dataset[key][i] : obj[key] = dataset[key][i]; });
        data.push(obj);
    });
    return data;
};

const mapScatterData = (dataset, aliases) => {
    // has two separate datasets
    let data1 = [];
    let data2 = [];

    if (Object.keys(dataset).length === 0) {
        return [data1, data2];
    }

    let objkeys = Object.keys(aliases);

    dataset.time.forEach((t, i) => {
        let obj1 = { time: t };
        let obj2 = { time: t };
        objkeys.forEach(key => {
            let datakey = aliases[key];
            key.includes('1') ? obj1[datakey] = dataset[key][i] : obj2[datakey] = dataset[key][i];
        });
        data1.push(obj1);
        data2.push(obj2);
    });

    return [data1, data2];
};

const mapLineDataForScatterChart = (dataset, ykey, aliases = null) => {
    let data_total = {};
    let objkeys = aliases ? Object.keys(aliases) : Object.keys(dataset);
    objkeys.forEach(key => {
        if (key === 'time') return;
        let data = []; //data to be pushed into data_total
        //let datakey = aliases? aliases[key] : key; //if aliases is provided it will be entry
        let datakey = key;
        dataset.time.forEach((t, i) => {
            let obj = { time: t };
            obj[ykey] = dataset[key][i];
            data.push(obj);
        });
        data_total[datakey] = data;
    });
    return data_total;
};

export {
    units,
    mass,
    length,
    hrattr,
    vdhattr,
    mapLineData,
    mapScatterData,
    mapLineDataForScatterChart,
    getMinMax,
    compareDomains
};
