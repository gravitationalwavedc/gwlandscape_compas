import React from 'react';
import { Card, Button } from 'react-bootstrap';

const PublicationCard = ({publication}) => <Card className="publication-card">
    <Card.Body>
        <Card.Title className='font-weight-bold'>{publication.title}</Card.Title>
        <Card.Subtitle>
            {`${publication.author} · ${publication.year}`}
        </Card.Subtitle>
        <Card.Text className='font-italic'>
            {publication.keywords.edges.map(({node}) => node.tag).join(', ')}
        </Card.Text>
        { publication.datasets ? 
        <Button variant='outline-primary'>
          Start interactive visualisation
        </Button> : 
        <Button variant='outline-primary' disabled>
                No available models
        </Button>}
    </Card.Body>
</Card>;

export default PublicationCard;
