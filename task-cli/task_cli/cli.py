"""
Task CLI - Command Line Interface
Main CLI commands for task management
"""

import click
import os
import sys
from tabulate import tabulate
from colorama import init, Fore, Style
from .api_client import APIClient
from .version import __version__

# Initialize colorama for Windows support
init(autoreset=True)

# Get API URL from environment or use default
API_URL = os.environ.get('TASK_API_URL', 'http://localhost:5000')


def get_client():
    """Get API client instance"""
    return APIClient(API_URL)


def print_success(message):
    """Print success message in green"""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message):
    """Print error message in red"""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}", err=True)


def print_info(message):
    """Print info message in blue"""
    click.echo(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def format_task_table(tasks):
    """Format tasks as a table"""
    if not tasks:
        return "No tasks found"
    
    # Prepare table data
    headers = ["ID", "Title", "Status", "Created"]
    rows = []
    
    for task in tasks:
        # Color code status
        status = task['status']
        if status == 'completed':
            status = f"{Fore.GREEN}{status}{Style.RESET_ALL}"
        elif status == 'in_progress':
            status = f"{Fore.YELLOW}{status}{Style.RESET_ALL}"
        else:
            status = f"{Fore.WHITE}{status}{Style.RESET_ALL}"
        
        rows.append([
            task['id'],
            task['title'][:50] + ('...' if len(task['title']) > 50 else ''),
            status,
            task['created_at'][:10]  # Just the date
        ])
    
    return tabulate(rows, headers=headers, tablefmt='simple')


@click.group()
@click.version_option(version=__version__, prog_name='task')
def cli():
    """Task Manager CLI - Manage your tasks from the command line"""
    pass


@cli.command()
@click.argument('title')
@click.option('--description', '-d', default='', help='Task description')
def add(title, description):
    """Add a new task
    
    Example: task add "Buy groceries" -d "Milk, eggs, bread"
    """
    try:
        client = get_client()
        task = client.create_task(title=title, description=description)
        print_success(f"Task created with ID: {task['id']}")
        click.echo(f"   Title: {task['title']}")
        if description:
            click.echo(f"   Description: {task['description']}")
    except Exception as e:
        print_error(f"Failed to create task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed']),
              help='Filter by status')
def list(status):
    """List all tasks
    
    Examples:
        task list
        task list --status pending
        task list -s completed
    """
    try:
        client = get_client()
        tasks = client.get_tasks(status=status)
        
        if not tasks:
            print_info("No tasks found")
        else:
            click.echo(f"\n{format_task_table(tasks)}\n")
            click.echo(f"Total: {len(tasks)} task(s)")
    except Exception as e:
        print_error(f"Failed to list tasks: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('task_id', type=int)
def show(task_id):
    """Show detailed information about a task
    
    Example: task show 123
    """
    try:
        client = get_client()
        task = client.get_task(task_id)
        
        click.echo(f"\n{Fore.CYAN}Task #{task['id']}{Style.RESET_ALL}")
        click.echo(f"{'─' * 60}")
        click.echo(f"Title:       {task['title']}")
        click.echo(f"Description: {task['description'] or '(none)'}")
        click.echo(f"Status:      {task['status']}")
        click.echo(f"Created:     {task['created_at']}")
        click.echo(f"Updated:     {task['updated_at']}")
        click.echo()
    except ValueError:
        print_error(f"Task {task_id} not found")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to get task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as completed
    
    Example: task complete 123
    """
    try:
        client = get_client()
        task = client.update_task(task_id, status='completed')
        print_success(f"Task {task_id} marked as completed")
        click.echo(f"   Title: {task['title']}")
    except ValueError:
        print_error(f"Task {task_id} not found")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to update task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--description', '-d', help='New description')
@click.option('--status', '-s', type=click.Choice(['pending', 'in_progress', 'completed']),
              help='New status')
def update(task_id, title, description, status):
    """Update a task
    
    Examples:
        task update 123 --title "New title"
        task update 123 -s in_progress
        task update 123 -t "Title" -d "Description" -s completed
    """
    if not any([title, description, status]):
        print_error("At least one field must be specified (--title, --description, or --status)")
        sys.exit(1)
    
    try:
        client = get_client()
        task = client.update_task(task_id, title=title, description=description, status=status)
        print_success(f"Task {task_id} updated")
        click.echo(f"   Title: {task['title']}")
        click.echo(f"   Status: {task['status']}")
    except ValueError:
        print_error(f"Task {task_id} not found")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to update task: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('task_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id):
    """Delete a task
    
    Example: task delete 123
    """
    try:
        client = get_client()
        client.delete_task(task_id)
        print_success(f"Task {task_id} deleted")
    except ValueError:
        print_error(f"Task {task_id} not found")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to delete task: {str(e)}")
        sys.exit(1)


@cli.command()
def stats():
    """Show task statistics
    
    Example: task stats
    """
    try:
        client = get_client()
        stats_data = client.get_stats()
        
        click.echo(f"\n{Fore.CYAN}Task Statistics{Style.RESET_ALL}")
        click.echo(f"{'─' * 40}")
        click.echo(f"Total tasks:      {stats_data.get('total', 0)}")
        click.echo(f"Pending:          {stats_data.get('pending', 0)}")
        click.echo(f"In progress:      {stats_data.get('in_progress', 0)}")
        click.echo(f"Completed:        {stats_data.get('completed', 0)}")
        click.echo()
    except Exception as e:
        print_error(f"Failed to get statistics: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    cli()