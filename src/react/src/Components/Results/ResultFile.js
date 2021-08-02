import React from 'react';
import {createFragmentContainer, graphql} from 'react-relay';
import filesize from 'filesize';

const downloadUrl = 'https://gwcloud.org.au/job/apiv1/file/?fileId=';

const ResultFile = ({file}) => 
    <tr>
        <td>
            {
                file.isDir ? file.path : (
                    <a 
                        href={downloadUrl + file.downloadId}
                        target="_blank" rel="noreferrer">
                        {file.path}
                    </a>
                )
            }
        </td>
        <td>{file.isDir ? 'Directory' : 'File'}</td>
        <td>{filesize(file.fileSize, {round: 0})}</td>
    </tr>;

export default createFragmentContainer(ResultFile, {
    file: graphql`
        fragment ResultFile_file on CompasResultFile {
            path
            isDir
            fileSize
            downloadId
        }
    `
});
