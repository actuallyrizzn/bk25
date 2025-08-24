"""
BK25 Conversation Memory

Simple, effective conversation and automation storage
No complex vector databases - just what actually works
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiosqlite


class ConversationMemory:
    """Manages conversation history and automation storage using SQLite"""
    
    def __init__(self, db_path: str = "./data/bk25.db"):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def initialize_database(self) -> None:
        """Initialize SQLite database"""
        try:
            # Ensure data directory exists
            data_dir = Path(self.db_path).parent
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Open database connection
            self.db = await aiosqlite.connect(self.db_path)
            
            # Create tables
            await self.create_tables()
            
            print("📚 BK25 memory initialized")
        except Exception as error:
            print(f"Database initialization error: {error}")
            raise
    
    async def create_tables(self) -> None:
        """Create database tables"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        # Conversations table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Automations table
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                description TEXT NOT NULL,
                script TEXT NOT NULL,
                documentation TEXT,
                filename TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_count INTEGER DEFAULT 0
            )
        """)
        
        # User patterns table (for learning)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.db.commit()
    
    async def add_message(self, role: str, content: str, context: Dict[str, Any] = None) -> int:
        """Add a message to conversation history"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        context_json = json.dumps(context or {})
        
        cursor = await self.db.execute(
            "INSERT INTO conversations (role, content, context) VALUES (?, ?, ?)",
            [role, content, context_json]
        )
        await self.db.commit()
        return cursor.lastrowid
    
    async def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for context"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            "SELECT role, content, context, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?",
            [limit]
        )
        rows = await cursor.fetchall()
        
        # Reverse to get chronological order
        messages = []
        for row in reversed(rows):
            messages.append({
                "role": row[0],
                "content": row[1],
                "context": json.loads(row[2] or "{}"),
                "timestamp": row[3]
            })
        
        return messages
    
    async def add_automation(self, automation: Dict[str, Any]) -> int:
        """Store generated automation"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute("""
            INSERT INTO automations 
            (platform, description, script, documentation, filename) 
            VALUES (?, ?, ?, ?, ?)
        """, [
            automation["platform"],
            automation["description"],
            automation["script"],
            automation.get("documentation", ""),
            automation.get("filename", "")
        ])
        await self.db.commit()
        return cursor.lastrowid
    
    async def find_similar_automations(
        self, 
        description: str, 
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Find similar automations (simple text matching for now)"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        query = """
            SELECT * FROM automations 
            WHERE description LIKE ? 
        """
        params = [f"%{description}%"]
        
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        
        query += " ORDER BY used_count DESC, created_at DESC LIMIT 5"
        
        cursor = await self.db.execute(query, params)
        rows = await cursor.fetchall()
        
        # Convert to dictionaries
        automations = []
        for row in rows:
            automations.append({
                "id": row[0],
                "platform": row[1],
                "description": row[2],
                "script": row[3],
                "documentation": row[4],
                "filename": row[5],
                "created_at": row[6],
                "used_count": row[7]
            })
        
        return automations
    
    async def increment_automation_usage(self, automation_id: int) -> int:
        """Increment usage count for an automation"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        cursor = await self.db.execute(
            "UPDATE automations SET used_count = used_count + 1 WHERE id = ?",
            [automation_id]
        )
        await self.db.commit()
        return cursor.rowcount
    
    async def add_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> int:
        """Store a learned pattern"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        pattern_data_json = json.dumps(pattern_data)
        
        # First, check if pattern already exists
        cursor = await self.db.execute(
            "SELECT id, frequency FROM patterns WHERE pattern_type = ? AND pattern_data = ?",
            [pattern_type, pattern_data_json]
        )
        row = await cursor.fetchone()
        
        if row:
            # Update existing pattern
            pattern_id, frequency = row
            await self.db.execute(
                "UPDATE patterns SET frequency = frequency + 1, last_used = CURRENT_TIMESTAMP WHERE id = ?",
                [pattern_id]
            )
            await self.db.commit()
            return pattern_id
        else:
            # Insert new pattern
            cursor = await self.db.execute(
                "INSERT INTO patterns (pattern_type, pattern_data) VALUES (?, ?)",
                [pattern_type, pattern_data_json]
            )
            await self.db.commit()
            return cursor.lastrowid
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        if not self.db:
            raise RuntimeError("Database not initialized")
        
        stats = {}
        
        # Count conversations
        cursor = await self.db.execute("SELECT COUNT(*) as count FROM conversations")
        row = await cursor.fetchone()
        stats["total_messages"] = row[0]
        
        # Count automations
        cursor = await self.db.execute("SELECT COUNT(*) as count FROM automations")
        row = await cursor.fetchone()
        stats["total_automations"] = row[0]
        
        # Get platform distribution
        cursor = await self.db.execute(
            "SELECT platform, COUNT(*) as count FROM automations GROUP BY platform"
        )
        rows = await cursor.fetchall()
        stats["platform_distribution"] = {row[0]: row[1] for row in rows}
        
        return stats
    
    async def close(self) -> None:
        """Close database connection"""
        if self.db:
            await self.db.close()
            self.db = None