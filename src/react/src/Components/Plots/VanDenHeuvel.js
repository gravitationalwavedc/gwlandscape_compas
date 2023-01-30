import React, { useState, useEffect } from 'react';
import { vdhattr } from './DataUtil';
import './VanDenHeuvel.css';

const DOMAIN = process.env.NODE_ENV !== 'development' ? '' : 'http://localhost:3004';

export default function VanDenHeuvel({ data }) {
    const [imageIndex, setImageIndex] = useState(null);
    const [eventSequenceIndex, setEventSequenceIndex] = useState(null);
    const [eventString, setEventString] = useState(null);

    //const eventIndex = [2, 26, 13, 49, 15, 51]; //should generate these
    const eventAlphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];

    const stellarTypes = [
        'MS',
        'MS',
        'HG', 'FGB', 'CHeB', 'EAGB', 'TPAGB', 'HeMS', 'HeHG',
        'HeGB', 'HeWD', 'COWD', 'ONeWD', 'NS', 'BH', 'MR'
    ];

    const vdhattrData = vdhattr(data);

    const getEvents = () => {
        let imageIndices = [];
        let sequenceIndices = [];
        let eventStrings = [];
        let isMerger = false;

        //Beginning of event
        sequenceIndices.push(0);
        imageIndices.push(2);
        eventStrings.push(`Zero-age main-sequence, metallicity Z=${vdhattrData.Z1[0]}`);

        //iterate through time sequence
        for (let i = 0; i < vdhattrData.time.length; i++) {
            if (i == 0) continue;
            //if (isMerger) break;

            let stype1 = vdhattrData.Stellar_Type1[i];
            let stype2 = vdhattrData.Stellar_Type2[i];

            //eventClass=='Mass Transfer'
            if (vdhattrData.MT_history[i] > 0 && vdhattrData.MT_history[i - 1] !== vdhattrData.MT_history[i]) {
                let image_num, eventstring;
                let mtValue = vdhattrData.MT_history[i];
                isMerger = true;

                switch (mtValue) {
                case 1:
                    eventstring = 'Stable mass transfer from 1 to 2';
                    if (stype2 < 13) {
                        image_num = 26;
                    } else {
                        image_num = 44;
                    }
                case 2:
                    eventstring = 'Stable mass transfer from 2 to 1';
                    if (stype2 < 13) {
                        image_num = 26;
                    } else {
                        image_num = 44;
                    }
                    break;
                case 3:
                case 4:
                    eventstring = `Common envelope initiated by ${Math.floor(mtValue / 2)}`;
                    image_num = (stype1 < 13 && stype2 < 13) ? 28 : 49;
                    break;
                case 5:
                    eventstring = 'Double-core common envelope';
                    image_num = 28;
                    break;
                case 6:
                    image_num = 37;
                    eventstring = `Stellar Merger: ${stellarTypes[stype1]}+${stellarTypes[stype2]}`;
                    break;
                default:
                    throw new Error('Unknow MT_history');
                }
                sequenceIndices.push(i);
                imageIndices.push(image_num);
                eventStrings.push(eventstring);
            }

            //eventClass = 'supernova' or 'stellar type change'
            let type_changed_star, isSupernova; //which star 

            if (stype1 !== vdhattrData.Stellar_Type1[i - 1]) {
                type_changed_star = 1;
                isSupernova = stype1 === 13 || stype1 === 14;
            }

            if (stype2 !== vdhattrData.Stellar_Type2[i - 1]) {
                type_changed_star = 2;
                isSupernova = stype2 === 13 || stype2 === 14;
            }

            if (type_changed_star) {
                let image_num, eventstring;
                //if supernova
                if (isSupernova) {
                    let remType = type_changed_star === 1 ? stype1 : stype2;
                    let comType = type_changed_star === 1 ? stype2 : stype1;
                    let disrupted = vdhattrData.eccentricity[i] > 1 || vdhattrData.semimajor[i] < 0;
                    eventstring = `Star ${remType} undergoes supernova and forms a ${stellarTypes[remType]} `
                        + `${disrupted ? '. Orbit becomes unbound' : ''}.`;
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
                let types = Array.from({ length: 5 }, (a, b) => b + 10);

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
                    let beta = 64 / 5 * G ** 3 * m1 * m2 * (m1 + m2) * Msunkg ** 3 / c ** 5;
                    let T0 = a ** 4 / 4 / beta;
                    let Tdelay = T0 * (1 - e ** 2) ** (7 / 2) * (
                        1 + 0.31 * e ** 10 + 0.27 * e ** 20 + 0.2 * e ** 1000) / 3.15e7 / 1e6;
                    eventstring = `Double compact object (${stellarTypes[stype1]}+${stellarTypes[stype2]}) merging in ${Tdelay.toFixed(2)} Myr`;
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
        setImageIndex(imageIndices);
        setEventSequenceIndex(sequenceIndices);
        setEventString(eventStrings);
    };

    useEffect(() => {
        getEvents();
    }, []);

    const imageDiv = (imageIndex = false) => {
        if (!imageIndex) return (<div className="cartoon" />);
        const filepath = `${DOMAIN}/compas/static/assets/${imageIndex}.png`;
        return (<div className="cartoon"><img src={filepath} /></div>);
    };

    const bebold = input => <b className="bold">{input}</b>;

    //index: eventIndex value, i: sequence number 
    const descDiv = (index, i) =>
    //let index = eventIndex[i];
        (
            <div className="desc">
            Time = {bebold(vdhattrData.time[index])} Myr, a = {bebold(vdhattrData.semimajor[index])} R<sub>⊙</sub>
                <br />
            M<sub>1</sub> = {bebold(vdhattrData.mass1[index])} M<sub>⊙</sub>,
            M<sub>2</sub> = {bebold(vdhattrData.mass2[index])} M<sub>⊙</sub>
                <br />
                {eventString[i]}
            </div>
        );


    const eventSequenceDiv = (i) => <div className="alphabet">{eventAlphabet[i]}</div>;

    return (<div>
        {eventSequenceIndex && eventSequenceIndex.map((index, i) =>
            <div className="container" key={i}>
                {imageIndex[i] && eventSequenceDiv(i)}
                {imageIndex[i] && imageDiv(imageIndex[i])}
                {imageIndex[i] && descDiv(index, i)}
            </div>
        )}
    </div>);
}
