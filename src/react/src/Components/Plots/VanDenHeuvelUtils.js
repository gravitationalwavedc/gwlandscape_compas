/* eslint-disable complexity */

export const eventAlphabet = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
    'U',
    'V',
    'W',
    'X',
    'Y',
    'Z',
];

export const stellarTypes = [
    'MS',
    'MS',
    'HG',
    'FGB',
    'CHeB',
    'EAGB',
    'TPAGB',
    'HeMS',
    'HeHG',
    'HeGB',
    'HeWD',
    'COWD',
    'ONeWD',
    'NS',
    'BH',
    'MR',
    'CHE',
];

const getEventString = (mtValue) => {
    const mtValueStrings = {
        1: 'Stable mass transfer from 1 to 2',
        2: 'Stable mass transfer from 2 to 1',
        4: `Common envelope initiated by ${Math.floor(mtValue / 2)}`,
        5: 'Double-core common envelope',
        6: 'Stellar Merger',
    };

    try {
        return mtValueStrings[mtValue];
    } catch (e) {
        throw new Error('Unknow MT_history', e);
    }
};

const getImageNumber = (mtValue, stype1, stype2) => {
    const mtValueImageNumbers = {
        1: stype2 < 13 ? 26 : 44,
        2: stype2 < 13 ? 26 : 44,
        4: stype1 < 13 && stype2 < 13 ? 28 : 49,
        5: 28,
        6: 37,
    };

    try {
        return mtValueImageNumbers[mtValue];
    } catch (e) {
        throw new Error('Unknow MT_history', e);
    }
};

const getWhichStar = (stype1, stype2, stellarType1, stellarType2) => {
    if (stype2 !== stellarType2) {
        return [2, stype2 === 13 || stype2 === 14];
    }

    if (stype1 !== stellarType1) {
        return [1, stype1 === 13 || stype1 === 14];
    }

    return [];
};

export const getEvents = (vdhattrData) => {
    let imageIndices = [2];
    let sequenceIndices = [0];
    let eventStrings = [`Zero-age main-sequence, metallicity Z=${vdhattrData.Z1[0]}`];
    let isMerger = false;

    for (let i = 0; i < vdhattrData.time.length; i++) {
        if (i === 0) continue;

        const stype1 = vdhattrData.Stellar_Type1[i];
        const stype2 = vdhattrData.Stellar_Type2[i];

        if (vdhattrData.MT_history[i] > 0 && vdhattrData.MT_history[i - 1] !== vdhattrData.MT_history[i]) {
            let mtValue = vdhattrData.MT_history[i];
            isMerger = true;
            sequenceIndices.push(i);
            imageIndices.push(getImageNumber(mtValue, stype1, stype2));
            eventStrings.push(getEventString(mtValue));
        }

        const [type_changed_star, isSupernova] = getWhichStar(
            stype1,
            stype2,
            vdhattrData.Stellar_Type1[i - 1],
            vdhattrData.Stellar_Type2[i - 1]
        ); //which star

        if (type_changed_star) {
            let image_num, eventstring;
            //if supernova
            if (isSupernova) {
                let remType = type_changed_star === 1 ? stype1 : stype2;
                let comType = type_changed_star === 1 ? stype2 : stype1;
                let disrupted = vdhattrData.eccentricity[i] > 1 || vdhattrData.semimajor[i] < 0;
                eventstring =
                    `Star ${type_changed_star} undergoes supernova and forms a ${stellarTypes[remType]} ` +
                    `${disrupted ? '. Orbit becomes unbound' : ''}.`;
                if (disrupted) {
                    if (comType < 13) {
                        image_num = remType === 13 ? 19 : 20;
                    } else if (comType === 13) {
                        image_num = remType === 13 ? 22 : 21;
                    } else {
                        image_num = remType === 13 ? 24 : 23;
                    }
                } else {
                    image_num = comType === 13 ? 13 : 15;
                }
            } else {
                let stypePre = vdhattrData[`Stellar_Type${type_changed_star}`][i - 1];
                let stypePost = vdhattrData[`Stellar_Type${type_changed_star}`][i];
                //no image_num
                eventstring = `Star ${type_changed_star}: ${stellarTypes[stypePre]} -> ${stellarTypes[stypePost]} `;
            }
            sequenceIndices.push(i);
            imageIndices.push(image_num);
            eventStrings.push(eventstring);
        }

        if (i === vdhattrData.time.length - 1 && !isMerger) {
            let eventstring, image_num;
            let isUnbound = vdhattrData.eccentricity[i] > 1 || vdhattrData.semimajor[i] < 0;
            let types = Array.from({ length: 5 }, (_, b) => b + 10);

            let isDCO = types.includes(stype1) && types.includes(stype2);
            if (isDCO) {
                let Msunkg = 1.98892e30;
                let c = 299792458;
                let G = 6.67428e-11;
                let Rsun = 695500000;
                let a = vdhattrData.semimajor[i] * Rsun;
                let e = vdhattrData.eccentricity[i];
                let m1 = vdhattrData.mass1[i];
                let m2 = vdhattrData.mass2[i];
                let beta = ((64 / 5) * G ** 3 * m1 * m2 * (m1 + m2) * Msunkg ** 3) / c ** 5;
                let T0 = a ** 4 / 4 / beta;
                let Tdelay =
                    (T0 * (1 - e ** 2) ** (7 / 2) * (1 + 0.31 * e ** 10 + 0.27 * e ** 20 + 0.2 * e ** 1000)) /
                    3.15e7 /
                    1e6;
                eventstring = `Double compact object (${stellarTypes[stype1]}+${
                    stellarTypes[stype2]
                }) merging in ${Tdelay.toFixed(2)} Myr`;
                if (stype1 === 13 && stype2 === 13) image_num = 55;
                else if (stype1 === 14 && stype2 === 14) image_num = 51;
                else image_num = 53;
            } else if (isUnbound) {
                eventstring = `Unbound : ${stellarTypes[stype1]}+${stellarTypes[stype2]}`;
            } else {
                eventstring = `Evolution ended by run duration: ${stellarTypes[stype1]}+${stellarTypes[stype2]}`;
                image_num = 2;
            }

            sequenceIndices.push(i);
            imageIndices.push(image_num);
            eventStrings.push(eventstring);
        }
    }

    return [imageIndices, sequenceIndices, eventStrings];
};
