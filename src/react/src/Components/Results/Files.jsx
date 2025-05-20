import React from 'react';
import {QueryRenderer, graphql} from 'react-relay';
import {harnessApi} from '../../index';
import {Table} from 'react-bootstrap';
import ResultFile from './ResultFile';

const Files = ({jobId}) =>

    <React.Fragment>
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
                            return <tr><td>{error.message}</td></tr>;
                        } else if (props && props.compasResultFiles) {
                            return <React.Fragment>
                                {
                                    props.compasResultFiles.files.map(
                                        (f, i) =>
                                            <ResultFile jobId={jobId} file={f} key={f.downloadToken}/>
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


export default Files;