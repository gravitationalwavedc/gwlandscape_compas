import React from 'react';
import Link from 'found/Link';
import { Card, Button } from 'react-bootstrap';

const PublicationCard = ({ publication, match, router }) => <Card className="publication-card">
  <Card.Body>
    <Card.Title className='font-weight-bold'>{publication.title}</Card.Title>
    <Card.Subtitle>
      {`${publication.author} · ${publication.year}`}
    </Card.Subtitle>
    <Card.Text className='font-italic'>
      {publication.keywords.edges.map(({ node }) => node.tag).join(', ')}
    </Card.Text>
    {
      publication.datasetModels.edges.length
        ? <Link
          as={Button}
          variant='outline-primary'
          key={publication.id}
          to={{ pathname: '/publication/' + publication.id + '/' }}
          exact
          match={match}
          router={router}
        >
          Start interactive visualisation
        </Link>
        : <Button variant='outline-primary' disabled>
          No available models
        </Button>
    }
  </Card.Body>
</Card>;

export default PublicationCard;
