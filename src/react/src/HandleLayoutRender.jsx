import Loading from './Components/Loading';

// Special render function for the Layout super-component
// This has to function slightly differently to the normal HandleRender since
// that function depends on the UserContext which is created by the Layout
const HandleLayoutRender = ({ Component, props }) => {
    if (!Component || !props) return <Loading />;
    return <Component data={props} {...props} />;
};

export default HandleLayoutRender;
