"""
Unit tests for Task CLI
Run with: pytest tests/test_cli.py -v
"""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from task_cli.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner"""
    return CliRunner()


@pytest.fixture
def mock_client():
    """Create mock API client"""
    with patch('task_cli.cli.get_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


def test_cli_version(runner):
    """Test version command"""
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert 'task' in result.output


def test_add_task(runner, mock_client):
    """Test adding a task"""
    mock_client.create_task.return_value = {
        'id': 1,
        'title': 'Test Task',
        'description': 'Test description',
        'status': 'pending'
    }
    
    result = runner.invoke(cli, ['add', 'Test Task', '-d', 'Test description'])
    assert result.exit_code == 0
    assert 'Task created' in result.output
    assert '1' in result.output
    
    mock_client.create_task.assert_called_once_with(
        title='Test Task',
        description='Test description'
    )


def test_list_tasks(runner, mock_client):
    """Test listing tasks"""
    mock_client.get_tasks.return_value = [
        {
            'id': 1,
            'title': 'Task 1',
            'status': 'pending',
            'created_at': '2025-01-01T10:00:00'
        },
        {
            'id': 2,
            'title': 'Task 2',
            'status': 'completed',
            'created_at': '2025-01-02T10:00:00'
        }
    ]
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'Task 1' in result.output
    assert 'Task 2' in result.output
    assert 'Total: 2' in result.output


def test_list_tasks_by_status(runner, mock_client):
    """Test filtering tasks by status"""
    mock_client.get_tasks.return_value = [
        {
            'id': 1,
            'title': 'Pending Task',
            'status': 'pending',
            'created_at': '2025-01-01T10:00:00'
        }
    ]
    
    result = runner.invoke(cli, ['list', '--status', 'pending'])
    assert result.exit_code == 0
    assert 'Pending Task' in result.output
    
    mock_client.get_tasks.assert_called_once_with(status='pending')


def test_list_tasks_empty(runner, mock_client):
    """Test listing when no tasks exist"""
    mock_client.get_tasks.return_value = []
    
    result = runner.invoke(cli, ['list'])
    assert result.exit_code == 0
    assert 'No tasks found' in result.output


def test_show_task(runner, mock_client):
    """Test showing task details"""
    mock_client.get_task.return_value = {
        'id': 1,
        'title': 'Test Task',
        'description': 'Test description',
        'status': 'pending',
        'created_at': '2025-01-01T10:00:00',
        'updated_at': '2025-01-01T10:00:00'
    }
    
    result = runner.invoke(cli, ['show', '1'])
    assert result.exit_code == 0
    assert 'Test Task' in result.output
    assert 'Test description' in result.output
    assert 'pending' in result.output


def test_complete_task(runner, mock_client):
    """Test marking task as completed"""
    mock_client.update_task.return_value = {
        'id': 1,
        'title': 'Test Task',
        'status': 'completed'
    }
    
    result = runner.invoke(cli, ['complete', '1'])
    assert result.exit_code == 0
    assert 'marked as completed' in result.output
    
    mock_client.update_task.assert_called_once_with(1, status='completed')


def test_update_task(runner, mock_client):
    """Test updating a task"""
    mock_client.update_task.return_value = {
        'id': 1,
        'title': 'Updated Title',
        'status': 'in_progress'
    }
    
    result = runner.invoke(cli, ['update', '1', '--title', 'Updated Title', '--status', 'in_progress'])
    assert result.exit_code == 0
    assert 'updated' in result.output
    
    mock_client.update_task.assert_called_once_with(
        1,
        title='Updated Title',
        description=None,
        status='in_progress'
    )


def test_update_task_no_fields(runner, mock_client):
    """Test updating task without specifying any fields"""
    result = runner.invoke(cli, ['update', '1'])
    assert result.exit_code == 1
    assert 'At least one field must be specified' in result.output


def test_delete_task(runner, mock_client):
    """Test deleting a task"""
    mock_client.delete_task.return_value = True
    
    result = runner.invoke(cli, ['delete', '1'], input='y\n')
    assert result.exit_code == 0
    assert 'deleted' in result.output
    
    mock_client.delete_task.assert_called_once_with(1)


def test_stats(runner, mock_client):
    """Test getting statistics"""
    mock_client.get_stats.return_value = {
        'total': 10,
        'pending': 5,
        'in_progress': 3,
        'completed': 2
    }
    
    result = runner.invoke(cli, ['stats'])
    assert result.exit_code == 0
    assert 'Total tasks:      10' in result.output
    assert 'Pending:          5' in result.output
    assert 'Completed:        2' in result.output