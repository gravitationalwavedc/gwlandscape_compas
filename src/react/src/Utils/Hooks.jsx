import environment from '../environment.js';
import { graphql, fetchQuery } from "react-relay";
import { useState, useEffect } from "react";

const TaskStatusQuery = graphql`
  query HooksTaskStatusQuery($taskId: String!) {
    celeryTaskStatus(taskId: $taskId) {
      status
      error
    }
  }
`;

function useTaskPolling(taskId, intervalMs = 1500) {
  const [task, setTask] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!taskId) {
      return;
    }

    const poll = () => {
      fetchQuery(environment, TaskStatusQuery, { taskId }).subscribe({
        next: ({ celeryTaskStatus }) => {
          setTask(celeryTaskStatus);

          if (
            celeryTaskStatus.status === "SUCCESS" ||
            celeryTaskStatus.status === "FAILURE" ||
            celeryTaskStatus.status === "TIMEOUT"
          ) {
            clearInterval(timer);
          }
        },
        error: err => {
          setError(err);
          clearInterval(timer);
        },
      });
    };

    poll(); // poll immediately

    const timer = setInterval(poll, intervalMs);

    return () => clearInterval(timer);
  }, [taskId, intervalMs]);

  return { task, error };
}

export default useTaskPolling;