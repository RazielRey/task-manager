# Task CLI

Command-line interface for Task Management API.

## Installation

```bash
pip install -e .
```

## Usage

### Set API URL

```bash
export TASK_API_URL=http://localhost:5000
```

### Commands

```bash
# Add a task
task add "Buy groceries" -d "Milk, eggs, bread"

# List all tasks
task list

# List by status
task list --status pending
task list --status completed

# Show task details
task show 123

# Mark as completed
task complete 123

# Update a task
task update 123 --title "New title"
task update 123 --status in_progress

# Delete a task
task delete 123

# Show statistics
task stats

# Show version
task --version
```

## Version Compatibility

This CLI checks API version compatibility on startup. If the API requires a newer CLI version, you'll see an error message prompting you to upgrade.