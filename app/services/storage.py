import sqlite3
from typing import Dict, List
from pathlib import Path
import json

DB_PATH = "nexus.db"


def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            vector_id INTEGER UNIQUE NOT NULL,
            content_type TEXT,
            encoding TEXT,
            text_length INTEGER,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vector_id ON documents(vector_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON documents(content_type)")

    conn.commit()
    conn.close()


def store_metadata(metadata: Dict, content: str) -> int:
    """Store document metadata and content"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO documents 
            (title, content, vector_id, content_type, encoding, metadata) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["title"],
                content,
                metadata["vector_id"],
                metadata.get("content_type"),
                metadata.get("encoding"),
                json.dumps(metadata.get("additional_metadata", {}))
            )
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_document_by_vector_id(vector_id: int) -> Dict:
    """Retrieve document metadata by vector_id"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, title, vector_id, created_at FROM documents WHERE vector_id = ?",
            (vector_id,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "vector_id": row[2],
                "created_at": row[3],
            }
        return None
    finally:
        conn.close()


def get_documents_by_vector_ids(vector_ids: List[int]) -> List[Dict]:
    """Retrieve multiple documents' metadata by vector_ids"""
    if not vector_ids:
        return []
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        placeholders = ",".join("?" * len(vector_ids))
        cursor.execute(
            f"""SELECT id, title, content, vector_id, content_type, encoding, metadata, created_at 
            FROM documents WHERE vector_id IN ({placeholders})
            ORDER BY CASE vector_id {' '.join(f'WHEN ? THEN {i}' for i in range(len(vector_ids)))} END""",
            vector_ids + vector_ids  # Double the vector_ids for both IN clause and ORDER BY
        )
        results = [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "vector_id": row[3],
            "content_type": row[4],
            "encoding": row[5],
            "metadata": json.loads(row[6]) if row[6] else {},
            "created_at": row[7]
        } for row in cursor.fetchall()]
        print(f"Retrieved {len(results)} documents from database")
        return results
    except Exception as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()


def get_document_by_id(doc_id: int) -> Dict:
    """Retrieve document by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, title, content, vector_id, content_type, encoding, metadata, created_at FROM documents WHERE id = ?",
            (doc_id,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "vector_id": row[3],
                "content_type": row[4],
                "encoding": row[5],
                "metadata": json.loads(row[6]) if row[6] else {},
                "created_at": row[7]
            }
        return None
    finally:
        conn.close()


# Initialize the database when the module is imported
init_db()
