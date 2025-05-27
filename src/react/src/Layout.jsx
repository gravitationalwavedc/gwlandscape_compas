import { graphql } from 'react-relay';
import { createFragmentContainer } from 'react-relay';
import Menu from './Components/Menu';
import Loading from './Components/Loading';

import { UserContext } from './sessionUser';

const Layout = ({ children, data }) => {
    if (data === null) {
        return <Loading />;
    }

    return (
        <UserContext.Provider value={data.sessionUser}>
            <header>
                <Menu name={data.sessionUser.name} isAuthenticated={data.sessionUser.isAuthenticated} />
            </header>
            <main className="h-100" style={{ paddingTop: '64px' }}>
                {children}
            </main>
        </UserContext.Provider>
    );
};

export default createFragmentContainer(Layout, {
    data: graphql`
        fragment Layout_sessionUser on Query {
            sessionUser {
                pk
                name
                authenticationMethod
                isAuthenticated
            }
        }
    `,
});
