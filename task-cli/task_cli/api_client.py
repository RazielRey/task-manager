"""
API Client for Task CLI
Handles all communication with the Task API
"""

import requests
import sys
from typing import Dict, List, Optional
from .version import __version__, MIN_API_VERSION, MAX_API_VERSION


class APIClient:
    """Client for interacting with Task API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'task-cli/{__version__}'
        })
        
        # Check version compatibility on init
        self._check_version_compatibility()
    
    def _check_version_compatibility(self):
        """Check if API version is compatible with this CLI version"""
        try:
            response = self.session.get(f'{self.base_url}/api/v1/version', timeout=5)
            response.raise_for_status()
            
            api_info = response.json()
            api_version = api_info.get('version', 'unknown')
            min_cli_version = api_info.get('min_cli_version', '0.0.0')
            
            # Check if API requires newer CLI
            if self._compare_versions(__version__, min_cli_version) < 0:
                print(f"❌ ERROR: CLI version mismatch")
                print(f"   Your CLI version: {__version__}")
                print(f"   API requires CLI: >={min_cli_version}")
                print(f"   API version: {api_version}")
                print(f"\n   Please upgrade: pip install --upgrade task-cli")
                sys.exit(1)
            
            # Check if CLI is too new for API
            if self._compare_versions(api_version, MIN_API_VERSION) < 0:
                print(f"❌ ERROR: API version too old")
                print(f"   Your CLI version: {__version__}")
                print(f"   CLI requires API: >={MIN_API_VERSION}")
                print(f"   API version: {api_version}")
                print(f"\n   Please upgrade the API server")
                sys.exit(1)
                
        except requests.exceptions.ConnectionError:
            print(f"❌ ERROR: Cannot connect to API at {self.base_url}")
            print(f"   Make sure the API server is running")
            sys.exit(1)
        except requests.exceptions.Timeout:
            print(f"❌ ERROR: API request timed out")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR: Failed to check API compatibility: {str(e)}")
            sys.exit(1)
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns: -1 if v1<v2, 0 if equal, 1 if v1>v2"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if p1 < p2:
                return -1
            elif p1 > p2:
                return 1
        
        return 0
    
    def _handle_response(self, response: requests.Response) -> Dict:
        """Handle API response and raise appropriate errors"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ValueError("Resource not found")
            elif response.status_code == 400:
                error_data = response.json()
                raise ValueError(error_data.get('error', 'Bad request'))
            else:
                raise Exception(f"API error: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def create_task(self, title: str, description: str = "") -> Dict:
        """Create a new task"""
        response = self.session.post(
            f'{self.base_url}/api/v1/tasks',
            json={'title': title, 'description': description}
        )
        data = self._handle_response(response)
        return data.get('task', {})
    
    def get_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """Get all tasks, optionally filtered by status"""
        params = {'status': status} if status else {}
        response = self.session.get(
            f'{self.base_url}/api/v1/tasks',
            params=params
        )
        data = self._handle_response(response)
        return data.get('tasks', [])
    
    def get_task(self, task_id: int) -> Dict:
        """Get a specific task"""
        response = self.session.get(f'{self.base_url}/api/v1/tasks/{task_id}')
        data = self._handle_response(response)
        return data.get('task', {})
    
    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, status: Optional[str] = None) -> Dict:
        """Update a task"""
        payload = {}
        if title is not None:
            payload['title'] = title
        if description is not None:
            payload['description'] = description
        if status is not None:
            payload['status'] = status
        
        response = self.session.put(
            f'{self.base_url}/api/v1/tasks/{task_id}',
            json=payload
        )
        data = self._handle_response(response)
        return data.get('task', {})
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        response = self.session.delete(f'{self.base_url}/api/v1/tasks/{task_id}')
        data = self._handle_response(response)
        return data.get('success', False)
    
    def get_stats(self) -> Dict:
        """Get task statistics"""
        response = self.session.get(f'{self.base_url}/api/v1/stats')
        data = self._handle_response(response)
        return data.get('stats', {})