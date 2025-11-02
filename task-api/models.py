"""
Database models for Task API
Uses SQLite for simplicity - no external database needed
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict


class Database:
    """Simple SQLite database handler"""
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with tasks table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn


class Task:
    """Task model with CRUD operations"""
    
    VALID_STATUSES = ['pending', 'in_progress', 'completed']
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, title: str, description: str = "") -> Dict:
        """Create a new task"""
        if not title or not title.strip():
            raise ValueError("Title is required")
        
        now = datetime.utcnow().isoformat()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (title.strip(), description, 'pending', now, now))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return self.get_by_id(task_id)
    
    def get_all(self, status: Optional[str] = None) -> List[Dict]:
        """Get all tasks, optionally filtered by status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if status:
            if status not in self.VALID_STATUSES:
                raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_by_id(self, task_id: int) -> Optional[Dict]:
        """Get a specific task by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update(self, task_id: int, title: Optional[str] = None, 
               description: Optional[str] = None, status: Optional[str] = None) -> Optional[Dict]:
        """Update a task"""
        task = self.get_by_id(task_id)
        if not task:
            return None
        
        if status and status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(self.VALID_STATUSES)}")
        
        now = datetime.utcnow().isoformat()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        updates = []
        params = []
        
        if title is not None:
            if not title.strip():
                raise ValueError("Title cannot be empty")
            updates.append("title = ?")
            params.append(title.strip())
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        
        updates.append("updated_at = ?")
        params.append(now)
        params.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return self.get_by_id(task_id)
    
    def delete(self, task_id: int) -> bool:
        """Delete a task"""
        task = self.get_by_id(task_id)
        if not task:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_stats(self) -> Dict:
        """Get task statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM tasks
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else {}