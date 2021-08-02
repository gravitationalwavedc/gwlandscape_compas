import React from 'react';
import {createFragmentContainer, graphql} from 'react-relay';
import ReviewJob from '../Forms/ReviewJob';

const Parameters = (props) => {
    const jobData = props.jobData ? props.jobData : props.parameters;
    const values = Object.keys(jobData).reduce((result, key) => {
        Object.keys(jobData[key]).map((item) => {
            result[item] = jobData[key][item];
        });
        return result;
    }, {});

    if (typeof values['ifo'] === 'string')
        values['ifo'] = JSON.parse(values['ifo']);

    return <ReviewJob values={values} />;
};

export default createFragmentContainer(Parameters, {
    jobData: graphql`
        fragment Parameters_jobData on CompasJobNode {
            data {
                startFrequencyBand
                minStartTime
                maxStartTime
                asini
                freqBand
                alpha
                delta
                orbitTp
                orbitPeriod 
                driftTime
                dFreq
            }
            search {
                searchStartTime
                searchTBlock
                searchCentralA0
                searchA0Band
                searchA0Bins
                searchCentralP
                searchPBand
                searchPBins
                searchCentralOrbitTp
                searchOrbitTpBand
                searchOrbitTpBins
                searchLLThreshold
            }
        }
    `
});
