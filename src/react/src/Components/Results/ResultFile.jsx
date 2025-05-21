import React from 'react';
import { commitMutation, graphql } from 'react-relay';
import environment from '../../environment';

const downloadUrl = 'https://jobcontroller.adacs.org.au/job/apiv1/file/?fileId=';

const generateFileDownloadIdMutation = graphql`
    mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
        generateFileDownloadIds(input: $input) {
            result
        }
    }
`;

const handleOnFileClick = (e, jobId, token) => {
    e.preventDefault();
    commitMutation(environment, {
        mutation: generateFileDownloadIdMutation,
        variables: {
            input: {
                jobId: jobId,
                downloadTokens: [token],
            },
        },
        onCompleted: (response, errors) => {
            if (errors) {
                alert('Error downloading file');
            } else {
                const link = document.createElement('a');
                link.href = downloadUrl + response.generateFileDownloadIds.result[0];
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }
        },
    });
};
const ResultFile = ({ jobId, file }) => (
    <tr>
        <td>
            {file.isDir ? (
                file.path
            ) : (
                <a href="#" onClick={(e) => handleOnFileClick(e, jobId, file.downloadToken)}>
                    {file.path}
                </a>
            )}
        </td>
        <td>{file.isDir ? 'Directory' : 'File'}</td>
        <td>{file.fileSize}</td>
    </tr>
);
export default ResultFile;
