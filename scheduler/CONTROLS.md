# Scheduler Dashboard Controls

The scheduler dashboard now includes comprehensive controls for managing crawl tasks.

## Control Buttons

### Top Toolbar Controls
1. **Run All Tasks** - Execute all active tasks immediately
2. **Stop All Tasks** - Disable all tasks (prevent automatic execution)
3. **Start All Tasks** - Enable all tasks (allow automatic execution)

### Individual Task Controls
Each task row includes action buttons:
1. **Play Button** - Run the task immediately
2. **Pause/Play Toggle** - Enable/disable the task
3. **Refresh Button** - Reset the task's schedule

## Functionality

### Run All Tasks
- Executes all active crawl tasks immediately
- Shows confirmation dialog before execution
- Updates task status to "running"

### Stop All Tasks
- Disables all tasks (sets `is_active = False`)
- Prevents automatic execution of scheduled tasks
- Useful for maintenance or when stopping data collection

### Start All Tasks
- Enables all tasks (sets `is_active = True`)
- Allows automatic execution of scheduled tasks
- Useful after maintenance to resume normal operation

### Individual Task Controls

#### Run Now
- Executes a specific task immediately
- Creates a log entry for the execution
- Updates task status to "running"

#### Enable/Disable Toggle
- Toggles the active status of a task
- When disabled, tasks won't execute automatically
- Visual indicator shows active/inactive status

#### Reset Schedule
- Resets the task's schedule to default timing
- Clears last run time
- Sets next run time based on frequency

## Status Indicators

### Task Status Badges
- **Success** (green) - Task completed successfully
- **Failed** (red) - Task encountered an error
- **Running** (yellow) - Task is currently executing
- **Pending** (gray) - Task is waiting to execute

### Active Status Badges
- **Active** (green) - Task is enabled and will run automatically
- **Inactive** (gray) - Task is disabled and won't run automatically

## Usage Examples

### Emergency Stop
1. Click "Stop All Tasks" to disable all scheduled tasks
2. Confirm the action in the dialog
3. All tasks will show as inactive

### Maintenance Mode
1. Disable specific tasks using individual toggle buttons
2. Perform maintenance on sources or systems
3. Re-enable tasks when maintenance is complete

### Immediate Data Collection
1. Click "Run All Tasks" to collect data immediately
2. Or run individual tasks using the play button
3. Monitor progress in the logs section

## Best Practices

1. **Use Stop All Tasks** before system maintenance
2. **Use Start All Tasks** after maintenance to resume normal operation
3. **Reset Schedule** if a task's timing seems incorrect
4. **Toggle Individual Tasks** for fine-grained control
5. **Run Individual Tasks** for immediate data collection without affecting other tasks

## API Endpoints

All controls use POST requests to the following endpoints:
- `/scheduler/run-task/<task_id>/` - Run individual task
- `/scheduler/run-scheduled/` - Run all tasks
- `/scheduler/toggle-status/<task_id>/` - Enable/disable task
- `/scheduler/reset-schedule/<task_id>/` - Reset task schedule
- `/scheduler/stop-all/` - Disable all tasks
- `/scheduler/start-all/` - Enable all tasks

Each endpoint requires CSRF protection and returns JSON responses.