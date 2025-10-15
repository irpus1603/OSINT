# Scheduler Dashboard Button Descriptions

## Toolbar Buttons

### Run All Tasks
- **Icon**: Play button (▶)
- **Function**: Execute all active crawl tasks immediately
- **Use Case**: When you need to collect data right now instead of waiting for scheduled runs
- **Confirmation**: No confirmation required
- **Effect**: All active tasks will start executing immediately

### Stop All Tasks
- **Icon**: Stop circle button (⏹)
- **Function**: Disable all crawl tasks to prevent automatic execution
- **Use Case**: Emergency stop, maintenance, or when pausing data collection
- **Confirmation**: Requires user confirmation
- **Effect**: All tasks will be marked as inactive; scheduled executions will be paused

### Start All Tasks
- **Icon**: Play circle button (⏯)
- **Function**: Enable all crawl tasks to allow automatic execution
- **Use Case**: Resume normal operations after maintenance or pause
- **Confirmation**: Requires user confirmation
- **Effect**: All tasks will be marked as active; scheduled executions will resume

### Stop Celery
- **Icon**: Power button (⏻)
- **Function**: Terminate all Celery processes (worker and beat scheduler)
- **Use Case**: Emergency shutdown, system restart, or process troubleshooting
- **Confirmation**: Requires user confirmation
- **Effect**: 
  - Celery worker processes are terminated
  - Celery beat scheduler is terminated
  - Running tasks are marked as failed in database
  - Running logs are updated with failure status

### Start Celery
- **Icon**: Refresh clockwise button (⟳)
- **Function**: Launch Celery processes (worker and beat scheduler)
- **Use Case**: Starting processes after shutdown or system restart
- **Confirmation**: Requires user confirmation
- **Effect**: 
  - Celery worker processes are started
  - Celery beat scheduler is started
  - Scheduled task execution is enabled

## Individual Task Buttons

### Run Now
- **Icon**: Play button (▶)
- **Function**: Execute this specific task immediately
- **Use Case**: When you need to run a specific task right now
- **Confirmation**: No confirmation required
- **Effect**: The selected task will start executing immediately

### Enable/Disable Task
- **Icon**: Pause button (⏸) when enabled / Play button (▶) when disabled
- **Function**: Toggle the active status of this specific task
- **Use Case**: 
  - Disable a problematic task temporarily
  - Re-enable a task after fixing issues
- **Confirmation**: No confirmation required
- **Effect**: 
  - When disabled: Task won't execute automatically
  - When enabled: Task will execute according to schedule

### Reset Schedule
- **Icon**: Refresh counterclockwise button (↺)
- **Function**: Reset this task's schedule to default timing
- **Use Case**: 
  - Fix scheduling issues
  - Reset task timing after maintenance
- **Confirmation**: Requires user confirmation
- **Effect**: 
  - Next run time is recalculated based on frequency
  - Last run time is cleared
  - Task status is reset to pending

### Cancel Task
- **Icon**: X button (✕)
- **Function**: Cancel this currently running task
- **Use Case**: 
  - Stop a task that's taking too long
  - Cancel a stuck or problematic task
- **Availability**: Only appears on tasks with "running" status
- **Confirmation**: Requires user confirmation
- **Effect**: 
  - Task status is updated to "failed"
  - Associated logs are updated with failure status
  - Error message "Task cancelled manually" is added

## Status Indicators

### Task Status Badges
- **Success** (green): Task completed without errors
- **Failed** (red): Task encountered errors or was cancelled
- **Running** (yellow): Task is currently executing
- **Pending** (gray): Task is waiting to execute

### Active Status Badges
- **Active** (green): Task is enabled and will run automatically
- **Inactive** (gray): Task is disabled and won't run automatically

### Process Status Badges
- **Celery Status**: Overall system status
  - Running (green): All processes are active
  - Stopped (red): Processes are not running
- **Worker Status**: Task execution process
  - Active (green): Worker is processing tasks
  - Inactive (gray): Worker is not running
- **Beat Status**: Scheduling process
  - Active (green): Scheduler is running
  - Inactive (gray): Scheduler is not running

## Best Practices

### Button Usage Guidelines

1. **Run Now**: Use for immediate data collection needs
2. **Enable/Disable**: Use for long-term task management
3. **Reset Schedule**: Use when task timing seems incorrect
4. **Cancel Task**: Use for stuck or problematic running tasks
5. **Stop All Tasks**: Use for system-wide pause
6. **Start All Tasks**: Use to resume normal operations
7. **Stop Celery**: Use for emergency shutdown or maintenance
8. **Start Celery**: Use to restart the entire system

### Safety Considerations

1. **Destructive Operations**: Stop All Tasks, Stop Celery, and Cancel Task require confirmation
2. **Process Awareness**: Stopping Celery affects the entire system
3. **Status Monitoring**: Always check status indicators after operations
4. **Database Consistency**: All operations update database to maintain accurate status

### Troubleshooting

1. **Tasks Not Running**: Check if Celery is running and tasks are enabled
2. **Stuck Tasks**: Use Cancel Task button to free up resources
3. **Scheduling Issues**: Use Reset Schedule to fix timing problems
4. **Process Problems**: Use Stop Celery then Start Celery to restart processes