import { useState } from 'react';
import { Row, Col, Button, Container, Table, Form, Alert } from 'react-bootstrap';
import { graphql, createFragmentContainer, commitMutation } from 'react-relay';
import FormCard from '../Components/Forms/FormCard';
import { CopyButton, CheckButton } from '../Components/CustomButtons';
import moment from 'moment';
import Environment from '../environment.js';

const APIToken = ({ data }) => {
  const [tokens, setTokens] = useState(data.listApiTokens);
  const [isCreatingToken, setIsCreatingToken] = useState(false);
  const [tokenName, setTokenName] = useState('');
  const [tokenCreationError, setTokenCreationError] = useState('');
  const [newlyCreatedToken, setNewlyCreatedToken] = useState(null);

  function revoke(id) {
    commitMutation(Environment, {
      mutation: graphql`
                mutation APITokenRevokeMutation($id: ID!) {
                    deleteApiToken(id: $id) {
                        success
                    }
                }
            `,
      variables: { id },
      onCompleted: (response) => {
        if (response && response.deleteApiToken.success === true) {
          setTokens(tokens.filter((e) => e.id !== id));
        }
      },
    });
  }
  function createToken(name) {
    setTokenCreationError('');
    commitMutation(Environment, {
      mutation: graphql`
                mutation APITokenCreateMutation($name: String) {
                    createApiToken(name: $name) {
                        id
                        token
                    }
                }
            `,
      variables: { name },
      onCompleted: (response) => {
        if (response && response.createApiToken.token) {
          setNewlyCreatedToken({
            id: response.createApiToken.id,
            token: response.createApiToken.token,
            name: name,
          });
          setTokens([
            {
              id: response.createApiToken.id,
              token: response.createApiToken.token,
              lastUsed: Date.now(),
              name: name,
            },
            ...tokens,
          ]);
          setIsCreatingToken(false);
          setTokenName('');
        }
      },
      onError: () => {
        setTokenCreationError(
          'An error occurred while creating the token - ensure you do not already have a token with the same name',
        );
      },
    });
  }

  const renderTokenActions = () => {
    if (newlyCreatedToken) {
      // Show the newly created token with copy button and warning
      return (
        <div className="mt-3">
          <div className="alert alert-warning">
            <strong>Warning:</strong> This is the only time this token will be visible.
            <div className="align-items-center mt-2">
              <code className="mr-4">{newlyCreatedToken.token}</code>
              <CopyButton
                variant="outline-secondary"
                content="Copy"
                copyContent={newlyCreatedToken.token}
              />
            </div>
          </div>
        </div>
      );
    } else if (isCreatingToken) {
      // Show the token name input form
      return (
        <Form
          onSubmit={(e) => {
            e.preventDefault();
            if (!tokenName.trim()) {
              setTokenCreationError('Token name cannot be empty');
              return;
            }
            createToken(tokenName);
          }}
          className="mt-3"
        >
          <Form.Group>
            <Form.Label>Token Name</Form.Label>
            <Form.Control
              type="text"
              value={tokenName}
              onChange={(e) => setTokenName(e.target.value)}
              isInvalid={!!tokenCreationError}
              placeholder="Enter a name for your token"
              autoFocus
              maxLength={64}
              style={{ textAlign: 'left' }}
            />
            <Form.Control.Feedback type="invalid">{tokenCreationError}</Form.Control.Feedback>
          </Form.Group>
          <div className="d-flex ">
            <Button variant="secondary" className="mr-2" onClick={() => setIsCreatingToken(false)}>
              Cancel
            </Button>
            <Button variant="primary" type="submit">
              Create
            </Button>
          </div>
        </Form>
      );
    } else {
      // Show the Create Token button
      return (
        <Button variant="primary" onClick={() => setIsCreatingToken(true)}>
          Create Token
        </Button>
      );
    }
  };

  return (
    <Container className="pt-5" fluid>
      <Row className="mb-3">
        <Col md={{ span: 8, offset: 2 }}>
          <h1>API Tokens</h1>
          <p>
            API tokens are used by{' '}
            <a
              href="https://gwlandscape-python.readthedocs.io/en/latest/"
              target="_blank"
              rel="noopener noreferrer"
            >
              gwcloud-python
            </a>{' '}
            to authenticate you, allowing you to view proprietary data and submit new jobs.
          </p>
          <FormCard title="Tokens">
            {tokens.length ? (
              <Table>
                <thead>
                  <tr>
                    <th>Token</th>
                    <th>Last Used</th>
                    <th>Revoke</th>
                  </tr>
                </thead>
                <tbody>
                  {tokens.map((e) => (
                    <tr key={e.token}>
                      <td className="align-items-center">{e.name}</td>
                      <td>
                        {moment(e.lastUsed).format()} ({moment(e.lastUsed).fromNow()})
                      </td>
                      <td>
                        <CheckButton
                          variant="text text-danger"
                          content="Revoke"
                          cancelContent="Revoke Token?"
                          onClick={() => revoke(e.id)}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            ) : (
              <p>You do not have any API tokens associated with your account.</p>
            )}

            {renderTokenActions()}
          </FormCard>
        </Col>
      </Row>
    </Container>
  );
};
export default createFragmentContainer(APIToken, {
  data: graphql`
        fragment APIToken_data on Query {
            listApiTokens {
                id
                name
                lastUsed
            }
        }
    `,
});
