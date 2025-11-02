"""
Unit tests for Task API
Run with: pytest tests/test_api.py -v
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Database


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    
    # Use in-memory database for tests
    test_db_path = ':memory:'
    os.environ['DB_PATH'] = test_db_path
    
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'version' in data


def test_version_endpoint(client):
    """Test version endpoint"""
    response = client.get('/api/v1/version')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'version' in data
    assert 'api_version' in data
    assert data['api_version'] == 'v1'


def test_create_task(client):
    """Test creating a task"""
    response = client.post('/api/v1/tasks', json={
        'title': 'Test Task',
        'description': 'This is a test task'
    })
    
    assert response.status_code == 201
    
    data = response.get_json()
    assert data['success'] is True
    assert data['task']['title'] == 'Test Task'
    assert data['task']['description'] == 'This is a test task'
    assert data['task']['status'] == 'pending'
    assert 'id' in data['task']


def test_create_task_without_title(client):
    """Test creating a task without title fails"""
    response = client.post('/api/v1/tasks', json={
        'description': 'Task without title'
    })
    
    assert response.status_code == 400
    
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


def test_get_all_tasks(client):
    """Test getting all tasks"""
    # Create some tasks first
    client.post('/api/v1/tasks', json={'title': 'Task 1'})
    client.post('/api/v1/tasks', json={'title': 'Task 2'})
    
    response = client.get('/api/v1/tasks')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 2
    assert len(data['tasks']) == 2


def test_get_task_by_id(client):
    """Test getting a specific task"""
    # Create a task
    create_response = client.post('/api/v1/tasks', json={
        'title': 'Specific Task'
    })
    task_id = create_response.get_json()['task']['id']
    
    # Get the task
    response = client.get(f'/api/v1/tasks/{task_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['task']['id'] == task_id
    assert data['task']['title'] == 'Specific Task'


def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist"""
    response = client.get('/api/v1/tasks/999')
    assert response.status_code == 404
    
    data = response.get_json()
    assert data['success'] is False


def test_update_task(client):
    """Test updating a task"""
    # Create a task
    create_response = client.post('/api/v1/tasks', json={
        'title': 'Original Title'
    })
    task_id = create_response.get_json()['task']['id']
    
    # Update the task
    response = client.put(f'/api/v1/tasks/{task_id}', json={
        'title': 'Updated Title',
        'status': 'completed'
    })
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['task']['title'] == 'Updated Title'
    assert data['task']['status'] == 'completed'


def test_update_task_invalid_status(client):
    """Test updating task with invalid status"""
    # Create a task
    create_response = client.post('/api/v1/tasks', json={
        'title': 'Test Task'
    })
    task_id = create_response.get_json()['task']['id']
    
    # Try to update with invalid status
    response = client.put(f'/api/v1/tasks/{task_id}', json={
        'status': 'invalid_status'
    })
    
    assert response.status_code == 400
    
    data = response.get_json()
    assert data['success'] is False


def test_delete_task(client):
    """Test deleting a task"""
    # Create a task
    create_response = client.post('/api/v1/tasks', json={
        'title': 'Task to Delete'
    })
    task_id = create_response.get_json()['task']['id']
    
    # Delete the task
    response = client.delete(f'/api/v1/tasks/{task_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    
    # Verify task is deleted
    get_response = client.get(f'/api/v1/tasks/{task_id}')
    assert get_response.status_code == 404


def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist"""
    response = client.delete('/api/v1/tasks/999')
    assert response.status_code == 404


def test_filter_tasks_by_status(client):
    """Test filtering tasks by status"""
    # Create tasks with different statuses
    task1_response = client.post('/api/v1/tasks', json={'title': 'Task 1'})
    task1_id = task1_response.get_json()['task']['id']
    
    client.post('/api/v1/tasks', json={'title': 'Task 2'})
    
    # Update task1 to completed
    client.put(f'/api/v1/tasks/{task1_id}', json={'status': 'completed'})
    
    # Get only pending tasks
    response = client.get('/api/v1/tasks?status=pending')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 1
    assert all(task['status'] == 'pending' for task in data['tasks'])


def test_get_stats(client):
    """Test getting task statistics"""
    # Create tasks
    task1_response = client.post('/api/v1/tasks', json={'title': 'Task 1'})
    task1_id = task1_response.get_json()['task']['id']
    
    client.post('/api/v1/tasks', json={'title': 'Task 2'})
    
    # Update one to completed
    client.put(f'/api/v1/tasks/{task1_id}', json={'status': 'completed'})
    
    # Get stats
    response = client.get('/api/v1/stats')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['success'] is True
    assert data['stats']['total'] == 2
    assert data['stats']['completed'] == 1
    assert data['stats']['pending'] == 1