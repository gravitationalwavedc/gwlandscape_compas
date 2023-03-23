import React from 'react';
import {QueryRenderer, graphql} from 'react-relay';
import {harnessApi} from '../../index';
import {Table} from 'react-bootstrap';

const Files = ({jobId}) => {

    return <React.Fragment>
        <Table>
            <thead>
                <tr>
                    <th>File Path</th>
                    <th>Type</th>
                    <th>File Size</th>
                </tr>
            </thead>
            <tbody>
                <QueryRenderer
                    environment={harnessApi.getEnvironment('compas')}
                    query={graphql`
                        query FilesQuery ($jobId: ID!) {
                            compasResultFiles(jobId: $jobId) {
                                files {
                                    path
                                    isDir
                                    fileSize
                                    downloadToken                    
                                }
                            }
                        }
                    `}
                    variables={{jobId: jobId}}
                    render={({error, props}) => {
                        if (error) {
                            return <tr><td><div>{error.message}</div></td></tr>;
                        } else if (props && props.compasResultFiles) {
                            return <React.Fragment>
                                {
                                    props.compasResultFiles.files.map(
                                        (f, i) =>
                                            <tr key={i}>
                                                <td>{f.path}</td>
                                                <td>{f.isDir? 'Directory': 'File'}</td>
                                                <td>{f.fileSize}</td>
                                            </tr>
                                    )
                                }
                            </React.Fragment>;
                        }
                    }
                    }
                />
            </tbody>
        </Table>
    </React.Fragment>;
};

export default Files;