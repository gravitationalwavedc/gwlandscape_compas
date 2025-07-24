import { Row, Col, Button, Container } from 'react-bootstrap';
import Link from 'found/Link';

const Error404 = ({ match, router }) => (
  <Container className="pt-5" fluid>
    <Row className="justify-content-center text-center">
      <Col md={8} lg={6}>
        <div className="mb-4">
          <h1 className="display-1 text-muted mb-0">404</h1>
          <h2 className="mb-3">Page Not Found</h2>
          <div className="lead text-muted mb-4">
            The page you're looking for doesn't exist or has been moved.
          </div>
        </div>

        <div className="mb-4">
          <div className="mb-3">Here are some helpful links to get you back on track:</div>
          <div className="d-flex flex-wrap justify-content-center gap-2">
            <Link
              as={Button}
              variant="primary"
              to="/"
              exact
              match={match}
              router={router}
              className="m-1"
            >
              Home
            </Link>
            <Link
              as={Button}
              variant="outline-primary"
              to="/publications/"
              exact
              match={match}
              router={router}
              className="m-1"
            >
              Publications
            </Link>
            <Link
              as={Button}
              variant="outline-primary"
              to="/single-binary-form/"
              exact
              match={match}
              router={router}
              className="m-1"
            >
              Simulate Binary
            </Link>
            <Link
              as={Button}
              variant="outline-primary"
              to="/job-form/"
              exact
              match={match}
              router={router}
              className="m-1"
            >
              Simulate Population
            </Link>
          </div>
        </div>

        <div className="text-muted">
          <small>
            If you believe this is an error, please check the URL or contact support.
          </small>
        </div>
      </Col>
    </Row>
  </Container>
);

export default Error404;
