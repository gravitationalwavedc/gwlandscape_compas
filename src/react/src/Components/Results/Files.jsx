import { QueryRenderer, graphql } from 'react-relay';
import { Table } from 'react-bootstrap';
import ResultFile from './ResultFile';
import environment from '../../environment';

const Files = ({ jobId }) => (
    <>
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
                    environment={environment}
                    query={graphql`
                        query FilesQuery($jobId: ID!) {
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
                    variables={{ jobId: jobId }}
                    render={({ error, props }) => {
                        if (error) {
                            return (
                                <tr>
                                    <td>{error.message}</td>
                                </tr>
                            );
                        } else if (props && props.compasResultFiles) {
                            return (
                                <>
                                    {props.compasResultFiles.files.map((f) => (
                                        <ResultFile jobId={jobId} file={f} key={f.downloadToken} />
                                    ))}
                                </>
                            );
                        }
                    }}
                />
            </tbody>
        </Table>
    </>
);

export default Files;
