import { useContext } from 'react';
import Loading from './Components/Loading';
import NewJob from './Pages/NewJob';
import ViewJob from './Pages/ViewJob';
import MyJobs from './Pages/MyJobs';
import { UserContext } from './sessionUser';

// List of components that require authentication
const PROTECTED_COMPONENTS = [ViewJob, NewJob, MyJobs];

const HandleRender = ({ Component, props, match }) => {
    const user = useContext(UserContext);
    if (user === null) {
        return <Loading />;
    }

    // redirect to login page for authentication if a route is protected
    if (!user.isAuthenticated && PROTECTED_COMPONENTS.includes(Component)) {
        window.location.replace(
            `${import.meta.env.VITE_BACKEND_URL}/sso/login/?next=${import.meta.env.VITE_FRONTEND_URL}${match.location.pathname}`,
        );
        return <Loading />;
    }
    if (!Component || !props) return <Loading />;
    return <Component data={props} {...props} />;
};

const HandleRenderWrapper = (props) => {
    return <HandleRender {...props} />;
};

export default HandleRenderWrapper;
