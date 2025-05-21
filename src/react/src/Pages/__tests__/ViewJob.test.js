import React from 'react';
import ViewJob from '../ViewJob';
import { graphql, QueryRenderer } from 'react-relay';
import { MockPayloadGenerator } from 'relay-test-utils';
import { render, waitFor } from '@testing-library/react';
import 'regenerator-runtime/runtime';

/* global global */

describe('view Compas Job details page', () => {
    const ViewJobRenderer = () => (
        <QueryRenderer
            environment={global.environment}
            query={graphql`
                query ViewJobTestQuery($jobId: ID!) @relay_test_operation {
                    ...ViewJob_data @arguments(jobId: $jobId)
                }
            `}
            variables={{
                jobId: 'Q29tcGFzSm9iTm9kZToxNTA=',
            }}
            render={({ error, props }) => {
                if (props) {
                    return <ViewJob data={props} />;
                } else if (error) {
                    return error.message;
                }
            }}
        />
    );

    const mockViewCompasJobReturn = {
        CompasJobNode() {
            return {
                id: 'Q29tcGFzSm9iTm9kZToxNTA=',
                user: 'Eman Ali',
                userId: 1,
                lastUpdated: '2023-04-27 23:58:34 UTC',
                start: {
                    name: 'my-test-job',
                    description: 'my first test job',
                    private: true,
                },
                jobStatus: {
                    name: 'Completed',
                    number: '500',
                },
                numberOfSystems: '10.0',
                minInitialMass: '5.0',
                maxInitialMass: '150.0',
                initialMassFunction: 'KROUPA',
                initialMassPower: '',
                metallicityDistribution: 'ZSOLAR',
                minMetallicity: '',
                maxMetallicity: '0.03',
                minMassRatio: '0.01',
                maxMassRatio: '1.0',
                massRatioDistribution: 'FLAT',
                minSemiMajorAxis: '0.01',
                maxSemiMajorAxis: '1000.0',
                semiMajorAxisDistribution: 'FLATINLOG',
                minOrbitalPeriod: '1.1',
                maxOrbitalPeriod: '1000.0',
                massTransferAngularMomentumLossPrescription: 'ISOTROPIC',
                massTransferAccretionEfficiencyPrescription: 'THERMAL',
                massTransferFa: '',
                commonEnvelopeAlpha: '1.0',
                commonEnvelopeLambdaPrescription: 'LAMBDA_NANJING',
                remnantMassPrescription: 'FRYER2012',
                fryerSupernovaEngine: 'DELAYED',
                kickVelocityDistribution: 'MAXWELLIAN',
                velocity1: '0.0',
                velocity2: '0.0',
            };
        },
    };

    const mockCompasJobResultsFiles = {
        CompasResultFile() {
            return {
                path: 'a_cool_path',
                isDir: false,
                fileSize: 1234,
                downloadId: 'anDownloadId',
            };
        },
    };

    it('should render the actual page', async () => {
        expect.hasAssertions();
        const { getByTestId, getAllByText, getByText } = render(<ViewJobRenderer />);
        await waitFor(() =>
            global.environment.mock.resolveMostRecentOperation((operation) =>
                MockPayloadGenerator.generate(operation, mockViewCompasJobReturn),
            ),
        );
        await waitFor(() =>
            global.environment.mock.resolveMostRecentOperation((operation) =>
                MockPayloadGenerator.generate(operation, mockCompasJobResultsFiles),
            ),
        );
        expect(getByText('my-test-job')).toBeInTheDocument();
        expect(getAllByText('a_cool_path')[0]).toBeInTheDocument();
        expect(getByTestId('jobInfo')).toHaveTextContent('Eman Ali');
        expect(getByTestId('jobInfo')).toHaveTextContent('Completed');
        expect(getByTestId('jobInfo')).toHaveTextContent('2023-04-27 23:58:34 UTC');
        expect(getByText('my first test job')).toBeInTheDocument();
    });
});
