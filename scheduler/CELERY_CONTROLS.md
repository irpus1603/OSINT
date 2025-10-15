# Celery Process Controls

The scheduler dashboard now includes controls for managing Celery processes directly from the web interface.

## New Control Buttons

### Top Toolbar Controls
1. **Run All Tasks** - Execute all active crawl tasks immediately
2. **Stop All Tasks** - Disable all crawl tasks (prevent automatic execution)
3. **Start All Tasks** - Enable all crawl tasks (allow automatic execution)
4. **Stop Celery** - Terminate all Celery processes (worker and beat)
5. **Start Celery** - Launch Celery processes (worker and beat)

## Celery Process Management

### Stop Celery
- **Function**: Terminates all running Celery processes
- **Processes Affected**: 
  - Celery Worker (task execution)
  - Celery Beat (task scheduling)
- **Use Case**: Emergency stop, maintenance, or process restart
- **Confirmation**: Requires user confirmation before execution
- **Effect**: Stops all scheduled task execution immediately

### Start Celery
- **Function**: Launches Celery processes in the background
- **Processes Started**:
  - Celery Worker (task execution)
  - Celery Beat (task scheduling)
- **Use Case**: Starting processes after shutdown or maintenance
- **Confirmation**: Requires user confirmation before execution
- **Effect**: Enables scheduled task execution

## Status Monitoring

### Celery Status Display
The dashboard shows real-time status of Celery processes:
- **Overall Status**: Running (green) or Stopped (red)
- **Worker Status**: Active (green) or Inactive (gray)
- **Beat Status**: Active (green) or Inactive (gray)

### Status Colors
- **Green**: Process is running/active
- **Red**: Overall system is stopped
- **Gray**: Process is inactive/stopped

## API Endpoints

### Process Control Endpoints
- `POST /scheduler/stop-celery/` - Stop all Celery processes
- `POST /scheduler/start-celery/` - Start Celery processes
- `GET /scheduler/celery-status/` - Get Celery process status

### Response Format
All endpoints return JSON responses:
```json
{
  "status": "success|error",
  "message": "Descriptive message",
  "workers_killed": 1,
  "beats_killed": 1
}
```

## Usage Scenarios

### Emergency Shutdown
1. Click "Stop Celery" to terminate all processes
2. Confirm the action in the dialog
3. Wait for processes to terminate
4. Verify status shows as "Stopped"

### Maintenance Restart
1. Perform system maintenance
2. Click "Start Celery" to launch processes
3. Confirm the action in the dialog
4. Wait for processes to start
5. Verify status shows as "Running"

### Process Monitoring
1. Check the status indicators regularly
2. Green badges indicate healthy processes
3. Red badges indicate stopped processes
4. Use controls to manage as needed

## Best Practices

### Before System Maintenance
1. Click "Stop Celery" to gracefully shut down processes
2. Wait for confirmation before proceeding
3. Perform maintenance tasks
4. Click "Start Celery" to resume operations

### Troubleshooting
1. If tasks aren't executing, check Celery status
2. If status shows "Stopped", click "Start Celery"
3. If problems persist, restart the processes
4. Monitor logs for error messages

### Process Management
1. Use "Stop Celery" for complete process shutdown
2. Use "Stop All Tasks" for task-level control without stopping processes
3. Use "Start Celery" to launch processes after shutdown
4. Regularly monitor status indicators

## Security Considerations

### Access Control
- Only authenticated users should access these controls
- Consider implementing role-based access control
- Log all process control actions for audit purposes

### Safe Operations
- All operations require user confirmation
- Processes are terminated gracefully when possible
- Error handling prevents system corruption

## Error Handling

### Common Issues
1. **Permission Denied**: Ensure proper file permissions
2. **Process Not Found**: Processes may have already terminated
3. **Startup Failures**: Check system resources and configurations

### Recovery
1. If start fails, check system logs
2. If stop fails, try manual process termination
3. If status is inconsistent, refresh the dashboard