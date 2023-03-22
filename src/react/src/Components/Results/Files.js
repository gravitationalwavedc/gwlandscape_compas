import React from 'react';
import {QueryRenderer, graphql} from 'react-relay';
import {harnessApi} from '../../index';

const Files = ({jobId}) => {

    return <React.Fragment>
        <QueryRenderer
            environment={harnessApi.getEnvironment('compas')}
            query={graphql`
                query FilesQuery ($jobId: ID!) {
                    compasResultFiles(jobId: $jobId) {
                        files {
                            path
                            downloadToken                          
                        }
                    }
                }
            `}
            variables={{jobId: jobId}}
            render={({error, props}) => {
                if (error) {
                    return <div>{error.message}</div>;
                } else if (props && props.compasResultFiles) {
                    return <ul>
                        {
                            props.compasResultFiles.files.map(
                                (f, i) => <li key={f.downloadToken}>{f.path}</li>
                            )
                        }
                    </ul>;

                }
            }
            }
        />
    </React.Fragment>;
};

export default Files;