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
import MyJobs from './Pages/MyJobs';
import PublicJobs from './Pages/PublicJobs';

// List of components that require authentication
const PROTECTED_COMPONENTS = [
    ViewJob,
    NewJob,
    MyJobs
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
                query={graphql`
                    query Routes_NewSingleBinaryJob_Query {
                        ...NewSingleBinaryJob_data
                    }
                `}
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
                        $publicationId: ID!
                        $datasetId: ID
                        $rootGroup: String
                        $subgroupX: String
                        $subgroupY: String
                        $strideLength: Int
                    ){
                        ...ViewPublication_data @arguments(
                            publicationId: $publicationId
                            datasetId: $datasetId
                        )
                    }
                `}
                prepareVariables={(params) => ({
                    publicationId: params.publicationId,
                })}
                render={handleRender}
            />
            <Route
                path="my-jobs"
                environment={harnessApi.getEnvironment('compas')}
                Component={MyJobs}
                query={graphql`
                    query Routes_MyJobs_Query(
                      $count: Int!,
                      $cursor: String,
                      $orderBy: String
                    ) {
                      ...MyJobs_data
                    }
                `}
                prepareVariables={() => ({
                    count: 10,
                    orderBy: '-lastUpdated'
                    // timeRange: 'all',
                })}
                render={handleRender}
            />
            <Route
                Component={PublicJobs}
                path="jobs"
                query={graphql`
                query Routes_PublicJobs_Query (
                  $count: Int!,
                  $cursor: String,
                  $search: String,
                ) {
                    ...PublicJobs_data
                }
              `}
                prepareVariables={() => ({
                    timeRange: 'all',
                    count: 10
                })}
                environment={harnessApi.getEnvironment('compas')}
                render={handleRender}/>
        </Route>
    );
}

export default getRoutes;
