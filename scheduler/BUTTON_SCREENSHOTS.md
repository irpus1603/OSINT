# Scheduler Dashboard - Button Descriptions

## Toolbar Buttons

![Toolbar Buttons](toolbar-buttons.png)

The toolbar contains five main control buttons:

1. **Run All Tasks** (Blue) - Execute all active tasks immediately
2. **Stop All Tasks** (Red) - Disable all tasks to prevent automatic execution
3. **Start All Tasks** (Green) - Enable all tasks to allow automatic execution
4. **Stop Celery** (Orange) - Terminate all Celery processes
5. **Start Celery** (Blue) - Launch Celery processes

Each button has a tooltip that appears when you hover over it, explaining its function.

## Individual Task Buttons

![Task Buttons](task-buttons.png)

Each task row contains a group of action buttons:

1. **Run Now** (Blue Play Icon ▶) - Execute this specific task immediately
   - Tooltip: "Run this task immediately"

2. **Enable/Disable Task** (Yellow Pause Icon ⏸ or Green Play Icon ▶)
   - When task is active: Yellow Pause button
     - Tooltip: "Disable this task"
   - When task is inactive: Green Play button
     - Tooltip: "Enable this task"

3. **Reset Schedule** (Light Blue Refresh Icon ↺)
   - Tooltip: "Reset task schedule"

4. **Cancel Task** (Red X Icon ✕) - Only appears for running tasks
   - Tooltip: "Cancel this running task"

## Status Indicators

![Status Indicators](status-indicators.png)

### Task Status Badges
- **Green Badge**: Completed successfully
- **Red Badge**: Failed or cancelled
- **Yellow Badge**: Currently running
- **Gray Badge**: Pending execution

### Active Status Badges
- **Green Badge**: Active (will run automatically)
- **Gray Badge**: Inactive (won't run automatically)

## Tooltip Examples

When you hover over any button, a tooltip appears with a description:

- **Run All Tasks**: "Run all active tasks immediately"
- **Stop All Tasks**: "Disable all tasks to prevent automatic execution"
- **Enable Task**: "Enable this task"
- **Reset Schedule**: "Reset task schedule"
- **Cancel Task**: "Cancel this running task"

## Best Practices for Using Buttons

### Immediate Actions
- Use **Run Now** for urgent data collection
- Use **Run All Tasks** for comprehensive immediate scraping

### Task Management
- Use **Enable/Disable** to control individual tasks long-term
- Use **Reset Schedule** when task timing seems off
- Use **Cancel Task** for stuck or problematic running tasks

### System Management
- Use **Stop All Tasks** for planned maintenance
- Use **Start All Tasks** to resume normal operations
- Use **Stop Celery** for emergency shutdown
- Use **Start Celery** to restart the entire system

## Safety Features

### Confirmation Dialogs
Several destructive operations require confirmation:
- Stop All Tasks
- Stop Celery
- Reset Schedule
- Cancel Task

### Visual Feedback
- Button colors indicate function (blue=neutral, green=start, red=stop, yellow=warning)
- Status badges show current state
- Hover tooltips explain actions before clicking

## Keyboard Accessibility

All buttons are accessible via keyboard navigation:
- Tab to navigate between buttons
- Enter/Space to activate buttons
- Escape to close confirmation dialogs

## Mobile Considerations

On touch devices:
- Tap and hold buttons to see tooltips
- Larger touch targets for easier interaction
- Responsive layout adapts to screen size