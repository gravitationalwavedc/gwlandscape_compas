import environment from '../environment.js';
import { graphql, fetchQuery } from 'react-relay';
import { useState, useEffect } from 'react';

const TaskStatusQuery = graphql`
    query HooksTaskStatusQuery($taskId: String!) {
        celeryTaskStatus(taskId: $taskId) {
            status
            error
        }
    }
`;

function useTaskPolling(taskId, intervalMs = 1500) {
    const [task, setTask] = useState({ id: taskId, status: null, error: null });
    const [error, setError] = useState(null);
    const [isPolling, setIsPolling] = useState(false);

    useEffect(() => {
        if (!taskId) {
            setTask({ id: taskId, status: null, error: null });
            setError(null);
            return;
        }

        const cleanup = (timer) => {
            setIsPolling(false);
            clearInterval(timer);
        };

        const poll = () => {
            fetchQuery(environment, TaskStatusQuery, { taskId }).subscribe({
                next: ({ celeryTaskStatus }) => {
                    setTask({ id: taskId, ...celeryTaskStatus });

                    if (
                        celeryTaskStatus.status === 'SUCCESS' ||
                        celeryTaskStatus.status === 'FAILURE' ||
                        celeryTaskStatus.status === 'TIMEOUT'
                    ) {
                        cleanup(timer);
                    }
                },
                error: (err) => {
                    setError(err);
                    cleanup(timer);
                },
            });
        };

        setIsPolling(true);

        poll(); // poll immediately

        const timer = setInterval(poll, intervalMs);

        return () => cleanup(timer);
    }, [taskId, intervalMs]);

    return {
        task: task.id === taskId ? task : { id: taskId, status: null, error: null },
        error,
        isPolling,
    };
}

export default useTaskPolling;
