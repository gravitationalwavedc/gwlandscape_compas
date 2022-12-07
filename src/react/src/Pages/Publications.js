import React, { useState, useEffect } from 'react';
import {createFragmentContainer, graphql} from 'react-relay';
import { Container, Col, Form, InputGroup, Row } from 'react-bootstrap';
import { HiOutlineSearch } from 'react-icons/hi';
import PublicationList from '../Components/PublicationList';
import searchPublications from '../Utils/searchPublications';


const Publications = ({data, match, router}) => {
    const [search, setSearch] = useState('');
    const [publications, setPublications] = useState();
    const allPublications = data && data.compasPublications ? data.compasPublications.edges.map(e => e.node) : null;
    
    useEffect(() => setPublications(allPublications), []);
    useEffect(() => handleSearchChange(), [search]);

    const handleSearchChange = () => {
        const filteredPublications = searchPublications(allPublications, search);
        setPublications(filteredPublications || allPublications);
    };

    return (
        <Container >
            <h1 className="pt-5 mb-4">
                Published Datasets
            </h1>
            <Form>
                <Form.Row>
                    <Col lg={6}>
                        <Form.Group controlId="searchJobs">
                            <Form.Label srOnly>
                              Search
                            </Form.Label>
                            <InputGroup>
                                <InputGroup.Prepend>
                                    <InputGroup.Text>
                                        <HiOutlineSearch />
                                    </InputGroup.Text>
                                </InputGroup.Prepend>
                                <Form.Control
                                    className="text-left"
                                    placeholder="Search by Author, Title, Keyword or Publication Date" 
                                    value={search} 
                                    onChange={({target}) => setSearch(target.value)} />
                            </InputGroup>
                        </Form.Group>
                    </Col>
                </Form.Row>
            </Form>
            <Row>
                <Col>
                    <PublicationList 
                        publications={publications}
                        match={match}
                        router={router}
                    />
                </Col>
            </Row>
        </Container>
    );
};

export default createFragmentContainer(Publications,
    {
        data: graphql`
            fragment Publications_data on Query {
                compasPublications {
                    edges {
                        node {
                            id
                            author
                            year
                            title
                            keywords {
                                edges {
                                    node {
                                        tag
                                    }
                                }
                            }
                        }
                    }
                }
            }
        `,
    }
);
