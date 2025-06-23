import { useState } from 'react';
import { commitMutation, createFragmentContainer, graphql } from 'react-relay';
import { Form } from 'react-bootstrap';
import environment from '../../environment';

const PrivacyToggle = (props) => {
    const [isPrivate, setIsPrivate] = useState(props.data.private);

    const handleChange = () => {
        const newValue = !isPrivate;
        setIsPrivate(newValue);
        updateJob(
            {
                jobId: props.jobId,
                private: newValue,
            },
            () => {},
        );
    };

    // TODO: AUTH
    const harnessApi = {
        currentUser: {
            userId: -1,
        },
    };
    return (
        <Form.Group className="mt-3" controlId="privateToggle">
            <Form.Check
                type="checkbox"
                label="Share with LIGO collaborators"
                onChange={handleChange}
                disabled={harnessApi.currentUser.userId !== props.userId}
                checked={!isPrivate}
            />
        </Form.Group>
    );
};

const updateJob = (variables, callback) =>
    commitMutation(environment, {
        mutation: graphql`
            mutation PrivacyToggleMutation($jobId: ID!, $private: Boolean, $labels: [String]) {
                updateCompasJob(input: { jobId: $jobId, private: $private, labels: $labels }) {
                    result
                }
            }
        `,
        optimisticResponse: {
            updateCompasJob: {
                result: 'Job saved!',
            },
        },
        variables: variables,
        onCompleted: (response, errors) => {
            if (errors) {
                callback(false, errors);
            } else {
                callback(true, response.updateCompasJob.result);
            }
        },
    });

export default createFragmentContainer(PrivacyToggle, {
    data: graphql`
        fragment PrivacyToggle_data on OutputStartType {
            private
        }
    `,
});
