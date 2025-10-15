# Task Cancellation and Process Management

The scheduler now includes comprehensive controls for managing both individual tasks and Celery processes, with proper status updates in the database.

## New Features

### Individual Task Cancellation
- **Cancel Button**: Red "X" button appears next to running tasks
- **Database Cleanup**: Cancels tasks and updates their status to "failed"
- **Log Updates**: Updates associated log entries with failure status
- **Confirmation**: Requires user confirmation before cancellation

### Celery Process Management
- **Stop Celery**: Terminates all Celery processes and updates database
- **Start Celery**: Launches Celery processes
- **Status Monitoring**: Real-time display of process status

## Database Status Updates

### When Stopping Celery
1. **Task Status**: Running tasks are updated to "failed"
2. **Log Status**: Running logs are updated to "failed"
3. **Timestamps**: Finished time is set to current time
4. **Error Messages**: Appropriate error messages are added

### When Cancelling Individual Tasks
1. **Task Status**: Specific task is updated to "failed"
2. **Log Status**: Associated running logs are updated to "failed"
3. **Timestamps**: Finished time is set to current time
4. **Error Messages**: "Task cancelled manually" message is added

## API Endpoints

### Task Cancellation
- `POST /scheduler/cancel-task/<task_id>/` - Cancel a specific running task

### Response Format
```json
{
  "status": "success",
  "message": "Task Task Name has been cancelled and marked as failed"
}
```

## Visual Indicators

### Task Status Badges
- **Running**: Yellow badge indicating active execution
- **Failed**: Red badge indicating cancelled or failed execution
- **Completed**: Green badge indicating successful completion
- **Pending**: Gray badge indicating waiting status

### Process Status Badges
- **Celery Status**: Overall system status (Running/Stopped)
- **Worker Status**: Celery worker process status
- **Beat Status**: Celery beat process status

## Usage Scenarios

### Cancelling a Stuck Task
1. Identify task with "running" status that won't complete
2. Click the red "X" cancel button
3. Confirm the cancellation
4. Task status updates to "failed" immediately
5. Associated logs are updated with failure information

### Emergency Process Shutdown
1. Click "Stop Celery" to terminate all processes
2. Confirm the action
3. All running tasks are automatically marked as "failed"
4. All running logs are updated with failure status
5. Process status indicators show "Stopped"

### Process Restart
1. Click "Start Celery" to launch processes
2. Confirm the action
3. Process status indicators show "Running"
4. Scheduled tasks will resume normal execution

## Error Handling

### Graceful Degradation
- If database updates fail, processes are still terminated
- Error messages are logged for debugging
- System remains functional even with partial failures

### Recovery
- After stopping Celery, running tasks won't actually be executing
- Database cleanup ensures accurate status representation
- Starting Celery enables future task execution

## Best Practices

### Task Management
1. Regularly monitor tasks with "running" status
2. Cancel tasks that appear stuck or unresponsive
3. Use process-level controls for system-wide operations
4. Monitor status indicators for system health

### Process Management
1. Stop Celery before system maintenance
2. Start Celery after maintenance is complete
3. Monitor process status for unexpected terminations
4. Use individual task cancellation for fine-grained control

## Security Considerations

### Access Control
- All operations require authentication
- CSRF protection prevents unauthorized requests
- Consider implementing role-based access for sensitive operations

### Audit Trail
- All cancellations and process operations are reflected in database
- Status changes provide historical tracking
- Error messages help with troubleshooting

## Troubleshooting

### Common Issues
1. **Tasks Still Show Running**: Database cleanup ensures accurate status
2. **Process Won't Stop**: Manual process termination may be required
3. **Status Inconsistencies**: Refresh dashboard to sync with actual state

### Recovery Steps
1. If status is inconsistent, refresh the dashboard
2. If processes won't stop, use system-level process management
3. If tasks won't cancel, check database connectivity