import React from 'react';
import {commitMutation, graphql} from 'react-relay';
import {harnessApi} from "../../index";
const downloadUrl = 'https://gwcloud.org.au/job/apiv1/file/?fileId=';

const generateFileDownloadIdMutation = graphql`
    mutation ResultFileMutation($input: GenerateFileDownloadIdsInput!) {
        generateFileDownloadIds(input: $input) {
            result
        }
    }
`;

const handleOnFileClick = (e, jobId, token) => {
    commitMutation(harnessApi.getEnvironment('compas'), {
        mutation: generateFileDownloadIdMutation,
        variables: {
            input: {
                jobId: jobId,
                downloadTokens: [token]
            }
        },
        onCompleted: (response, errors) => {
            if(errors) {
                alert('Unable to download file');
            } else {
                const link = e.target;
                link.href = downloadUrl + response.generateFileDownloadIds.result[0];
                link.click();
            }
        }
    });
    e.preventDefault();
};
const ResultFile = ({jobId, file}) =>
    <tr>
        <td>
            {
                file.isDir ? file.path : (
                    <a
                        href="#"
                        onClick={e => handleOnFileClick(e, jobId, file.downloadToken)}
                    >
                        {file.path}
                    </a>
                )

            }
        </td>
    </tr>;
export default ResultFile;