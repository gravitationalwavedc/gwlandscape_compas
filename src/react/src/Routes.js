import React from 'react';
import {Route} from 'found';
import MyJobs from './Pages/MyJobs';
import PublicJobs from './Pages/PublicJobs';
import {graphql} from 'react-relay';
import {harnessApi} from './index';
import Loading from './Components/Loading';
import {RedirectException} from 'found';
import NewSingleBinaryJob from './Pages/NewSingleBinaryJob';
import Home from './Pages/Home';
import Publications from './Pages/Publications';
import NewJob from './Pages/NewJob';

const handleRender = ({Component, props}) => {
    if (!Component || !props)
        return <Loading/>;

    if (! Component === NewSingleBinaryJob)
        if (!harnessApi.hasAuthToken())
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
                path='public-job-list'
                Component={PublicJobs}
                query={graphql`
                query Routes_HomePage_Query (
                  $count: Int!,
                  $cursor: String,
                  $search: String,
                  $timeRange: String,
                ) {
                    gwclouduser {
                      username
                    }
                    ...PublicJobs_data
                }
              `}
                prepareVariables={() => ({
                    timeRange: 'all',
                    count: 100
                })}
                environment={harnessApi.getEnvironment('compas')}
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
                path="job-list"
                query={graphql`
                query Routes_JobList_Query(
                    $count: Int!,
                    $cursor: String,
                    $orderBy: String
                    ) {
                        ...MyJobs_data
                    }
                    `}
                prepareVariables={() => ({
                    count: 100,
                    timeRange: 'all',
                })}
                    
                environment={harnessApi.getEnvironment('compas')}
                Component={MyJobs}
                render={handleRender}/>
            <Route
                path="single-binary-form"
                environment={harnessApi.getEnvironment('compas')}
                Component={NewSingleBinaryJob}
                render={handleRender}/>
        </Route>
    );
}

export default getRoutes;
