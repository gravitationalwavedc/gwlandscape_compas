import { Route } from 'found';
import { graphql } from 'react-relay';
import NewSingleBinaryJob from './Pages/NewSingleBinaryJob';
import Home from './Pages/Home';
import Publications from './Pages/Publications';
import NewJob from './Pages/NewJob';
import ViewJob from './Pages/ViewJob';
import ViewPublication from './Pages/ViewPublication';
import MyJobs from './Pages/MyJobs';
import PublicJobs from './Pages/PublicJobs';
import Layout from './Layout';
import HandleRender from './HandleRender';
import HandleLayoutRender from './HandleLayoutRender';
import APIToken from './Pages/APIToken';

function getRoutes() {
  return (
    <Route
      path="/"
      Component={Layout}
      render={HandleLayoutRender}
      query={graphql`
                query Routes_Layout_Query {
                    ...Layout_sessionUser
                }
            `}
    >
      <Route Component={Home} render={HandleRender} />
      <Route path="job-form" Component={NewJob} render={HandleRender} />

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
        Component={Publications}
        render={HandleRender}
      />
      <Route
        path="single-binary-form"
        Component={NewSingleBinaryJob}
        query={graphql`
                    query Routes_NewSingleBinaryJob_Query {
                        ...NewSingleBinaryJob_data
                    }
                `}
        render={HandleRender}
      />
      <Route
        path="job-results/:jobId/"
        Component={ViewJob}
        query={graphql`
                    query Routes_ViewJob_Query($jobId: ID!) {
                        ...ViewJob_data @arguments(jobId: $jobId)
                    }
                `}
        prepareVariables={(params) => ({
          jobId: params.jobId,
        })}
        render={HandleRender}
      />
      <Route
        path="publication/:publicationId/"
        Component={ViewPublication}
        query={graphql`
                    query Routes_ViewPublication_Query(
                        $publicationId: ID!
                        $datasetId: ID
                        $rootGroup: String
                        $subgroupX: String
                        $subgroupY: String
                        $strideLength: Int
                    ) {
                        ...ViewPublication_data @arguments(publicationId: $publicationId, datasetId: $datasetId)
                    }
                `}
        prepareVariables={(params) => ({
          publicationId: params.publicationId,
        })}
        render={HandleRender}
      />
      <Route
        path="my-jobs"
        Component={MyJobs}
        query={graphql`
                    query Routes_MyJobs_Query($count: Int!, $cursor: String, $orderBy: String) {
                        ...MyJobs_data
                    }
                `}
        prepareVariables={() => ({
          count: 10,
          orderBY: '-lastUpdated',
          // timeRange: 'all',
        })}
        render={HandleRender}
      />
      <Route
        Component={PublicJobs}
        path="jobs"
        query={graphql`
                    query Routes_PublicJobs_Query($count: Int!, $cursor: String, $search: String) {
                        ...PublicJobs_data
                    }
                `}
        prepareVariables={() => ({
          timeRange: 'all',
          count: 10,
        })}
        render={HandleRender}
      />
      <Route
        Component={APIToken}
        path="api-token"
        query={graphql`
                  query Routes_APIToken_Query {
                      ...APIToken_data
                  }`}
        render={HandleRender} />
    </Route>
  );
}

export default getRoutes;
