import { Link } from 'found';
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import GWLandscapeLogo from '../assets/images/GWLandscape-logo.svg';

const iconStyle = {
    height: '50px',
    margin: '-2px 2px 0 0',
};

const subMenu = (name) => {
    if (name) {
        return (
            <Nav>
                <Nav.Link to="/" as={Link}>
                    Home
                </Nav.Link>
                <Nav.Link to="/my-jobs/" as={Link}>
                    Jobs
                </Nav.Link>
                <Nav.Link to="/single-binary-form/" as={Link}>
                    Binary evolution
                </Nav.Link>
                <Nav.Link to="/publications/" as={Link}>
                    Published Datasets
                </Nav.Link>
                <Nav.Link href="https://gwlandscape-python.readthedocs.io/en/latest/gettingstarted.html">API</Nav.Link>
                <Nav.Link onClick={() => undefined}>Logout</Nav.Link>
            </Nav>
        );
    }

    return (
        <Nav>
            <Link to="/auth/" exact>
                Login
            </Link>
        </Nav>
    );
};

const Menu = ({ name }) => {
    const SubMenu = subMenu(name);
    return (
        <Navbar fixed="top" className="gwlandscape-menu">
            <Navbar.Brand className="mr-auto">
                <Link to="/" exact className="navbar-brand-link" data-testid="GWLandscapeLogo">
                    <img src={GWLandscapeLogo} style={iconStyle} />
                </Link>
            </Navbar.Brand>
            {SubMenu}
        </Navbar>
    );
};

export default Menu;
