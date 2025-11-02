"""
Task Management API - Flask Application
RESTful API for managing tasks with full CRUD operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from models import Database, Task
from version import __version__, get_version_info

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db_path = os.environ.get('DB_PATH', 'tasks.db')
db = Database(db_path)
task_model = Task(db)

# API version prefix
API_PREFIX = '/api/v1'


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes readiness/liveness probes"""
    return jsonify({
        'status': 'healthy',
        'version': __version__
    }), 200


@app.route(f'{API_PREFIX}/version', methods=['GET'])
def version():
    """Get API version information"""
    return jsonify(get_version_info()), 200


@app.route(f'{API_PREFIX}/tasks', methods=['GET'])
def get_tasks():
    """
    Get all tasks, optionally filtered by status
    Query params:
        - status: Filter by task status (pending, in_progress, completed)
    """
    try:
        status = request.args.get('status')
        tasks = task_model.get_all(status=status)
        
        logger.info(f"Retrieved {len(tasks)} tasks" + (f" with status={status}" if status else ""))
        
        return jsonify({
            'success': True,
            'count': len(tasks),
            'tasks': tasks
        }), 200
        
    except ValueError as e:
        logger.warning(f"Invalid status parameter: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route(f'{API_PREFIX}/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        task = task_model.get_by_id(task_id)
        
        if not task:
            logger.warning(f"Task {task_id} not found")
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        logger.info(f"Retrieved task {task_id}")
        
        return jsonify({
            'success': True,
            'task': task
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route(f'{API_PREFIX}/tasks', methods=['POST'])
def create_task():
    """
    Create a new task
    Request body:
        - title (required): Task title
        - description (optional): Task description
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        title = data.get('title')
        description = data.get('description', '')
        
        if not title:
            return jsonify({
                'success': False,
                'error': 'Title is required'
            }), 400
        
        task = task_model.create(title=title, description=description)
        
        logger.info(f"Created task {task['id']}: {title}")
        
        return jsonify({
            'success': True,
            'task': task
        }), 201
        
    except ValueError as e:
        logger.warning(f"Invalid task data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route(f'{API_PREFIX}/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Update a task
    Request body (all optional):
        - title: New task title
        - description: New description
        - status: New status (pending, in_progress, completed)
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400
        
        task = task_model.update(
            task_id=task_id,
            title=data.get('title'),
            description=data.get('description'),
            status=data.get('status')
        )
        
        if not task:
            logger.warning(f"Task {task_id} not found for update")
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        logger.info(f"Updated task {task_id}")
        
        return jsonify({
            'success': True,
            'task': task
        }), 200
        
    except ValueError as e:
        logger.warning(f"Invalid update data: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route(f'{API_PREFIX}/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        success = task_model.delete(task_id)
        
        if not success:
            logger.warning(f"Task {task_id} not found for deletion")
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        logger.info(f"Deleted task {task_id}")
        
        return jsonify({
            'success': True,
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route(f'{API_PREFIX}/stats', methods=['GET'])
def get_stats():
    """Get task statistics"""
    try:
        stats = task_model.get_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method not allowed'
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Task API v{__version__} on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)