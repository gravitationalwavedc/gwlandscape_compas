import React from 'react';
import PublicationCard from './PublicationCard';

const PublicationList = ({publications, match, router}) => 
    <>
        {
            publications && publications.length > 0 
                ? publications.map(
                    (publication) => <PublicationCard
                        key={publication.id}
                        publication={publication}
                        match={match} router={router}
                    />
                )
                : <div>No publications have been uploaded.</div>
        }
    </>;


export default PublicationList;
