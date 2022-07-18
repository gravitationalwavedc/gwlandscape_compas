import React from 'react';
import { Card, Button } from 'react-bootstrap';

const PublicationCard = ({publication}) => <Card>
    <Card.Body>
        <Card.Title className='font-weight-bold'>{publication.title}</Card.Title>
        <Card.Subtitle>
            {`${publication.author} - ${publication.year}`}
        </Card.Subtitle>
        <Card.Text className='font-italic'>
            {publication.keywords.edges.map(({node}) => node.tag).join(', ')}
        </Card.Text>
        <Button variant='outline-primary'>
                No available models
        </Button>
    </Card.Body>
</Card>;

export default PublicationCard;