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
        self.__init__db__()

    def init_db(self):
        """Initialize the database and create tables if they don't exist"""
        