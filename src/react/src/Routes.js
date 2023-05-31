import React from 'react';
import { Route } from 'found';
import { graphql } from 'react-relay';
import { harnessApi } from './index';
import Loading from './Components/Loading';
import { RedirectException } from 'found';
import NewSingleBinaryJob from './Pages/NewSingleBinaryJob';
import Home from './Pages/Home';
import Publications from './Pages/Publications';
import NewJob from './Pages/NewJob';
import ViewJob from './Pages/ViewJob';
import ViewPublication from './Pages/ViewPublication';

// List of components that require authentication
const PROTECTED_COMPONENTS = [
    ViewJob,
    NewJob
];

const handleRender = ({ Component, props }) => {
    if (!Component || !props)
        return <Loading/>;

    // redirect to login page for authentication if a route is protected
    if (!harnessApi.hasAuthToken() && PROTECTED_COMPONENTS.includes(Component))
        throw new RedirectException('/auth/?next=' + props.match.location.pathname);

    return <Component data={props} {...props}/>;
};

function getRoutes() {
    return (
        <Route>
            <Route
                Component={Home}
                environment={harnessApi.getEnvironment('compas')}
                render={handleRender}/>
            <Route
                path="job-form"
                Component={NewJob}
                render={handleRender}/>

            <Route
                path="publications"
                query={graphql`
                    query Routes_Publications_Query {
                        ...Publications_data
                    }
                `}
                prepareVariables={() => ({
                    count: 100,
                })}
                environment={harnessApi.getEnvironment('compas')}
                Component={Publications}
                render={handleRender}/>
            <Route
                path="single-binary-form"
                environment={harnessApi.getEnvironment('compas')}
                Component={NewSingleBinaryJob}
                render={handleRender}/>
            <Route
                path="job-results/:jobId/"
                environment={harnessApi.getEnvironment('compas')}
                Component={ViewJob}
                query={graphql`
                    query Routes_ViewJob_Query($jobId: ID!){
                        ...ViewJob_data @arguments(jobId: $jobId)
                    }
                `}
                prepareVariables={(params) => ({
                    jobId: params.jobId
                })}
                render={handleRender}
            />
            <Route
                path="publication/:publicationId/"
                environment={harnessApi.getEnvironment('compas')}
                Component={ViewPublication}
                query={graphql`
                    query Routes_ViewPublication_Query(
                        $publicationId: ID!,
                        $rootGroup: String
                        $subgroupX: String
                        $subgroupY: String
                        $strideLength: Int
                    ){
                        ...ViewPublication_data @arguments(
                            publicationId: $publicationId
                        )
                    }
                `}
                prepareVariables={(params) => ({
                    publicationId: params.publicationId,
                    rootGroup: 'BSE_Common_Envelopes',
                })}
                render={handleRender}
            />
        </Route>
    );
}

export default getRoutes;
