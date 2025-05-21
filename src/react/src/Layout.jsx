import React from 'react';
// import { graphql } from 'react-relay';
// import { createFragmentContainer } from 'react-relay';
import Menu from './Components/Menu';

// regex list to match urls where the menu should be hidden.
const noMenuURLs = [/\/auth\/(?!api-token).*/];

const Layout = ({ children, match }) => {
    // TODO: Auth
    // const name = "Frank Walker"
    const name = '';
    const showMenu = !noMenuURLs.some((regex) => regex.test(match.location.pathname));

    return (
        <>
            {showMenu && (
                <header>
                    <Menu name={name} match={match} />
                </header>
            )}
            <main className="h-100" style={showMenu ? { paddingTop: '64px' } : null}>
                {children}
            </main>
        </>
    );
};

export default Layout;

// export default createFragmentContainer(Layout, {
//   gwclouduser: graphql`
//         fragment Layout_gwclouduser on UserDetails {
//           userId
//           username
//           firstName
//           lastName
//           isLigoUser
//         }
//     `
// });
