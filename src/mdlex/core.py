import sqlite3
import json
import yaml
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, List
import re
import argparse

def init_db(db_path: str) -> sqlite3.Connection:
    """Initialize SQLite database and return connection"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE,
            frontmatter JSON,
            content TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_filepath ON documents(filepath)")
    conn.commit()

    return conn

def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML front matter from markdown content"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            return frontmatter or {}, match.group(2)
        except yaml.YAMLError as e:
            print(f"Warning: Failed to parse YAML frontmatter: {e}")
            return {}, content
    return {}, content

def serialize_dates(obj: Any) -> str:
    """Serialize dates to ISO format for JSON encoding"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def load_docs(conn: sqlite3.Connection, directory: str) -> int:
    """Recursively load markdown files into SQLite database"""
    cursor = conn.cursor()
    directory = Path(directory).resolve()
    docs_processed = 0

    for filepath in directory.rglob("*.md"):
        try:
            with filepath.open('r', encoding='utf-8') as f:
                content = f.read()

            frontmatter, markdown_content = extract_frontmatter(content)
            frontmatter_json = json.dumps(frontmatter, default=serialize_dates)

            cursor.execute("""
                INSERT INTO documents (filepath, frontmatter, content)
                VALUES (?, ?, ?)
                ON CONFLICT(filepath) DO UPDATE SET
                    frontmatter = excluded.frontmatter,
                    content = excluded.content
            """, (str(filepath), frontmatter_json, markdown_content))

            docs_processed += 1

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    conn.commit()
    return docs_processed

def query_db(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and return results"""
    cursor = conn.cursor()
    cursor.execute(sql, params)
    return [dict(row) for row in cursor.fetchall()]

def get_db_path(args_db_path: str | None) -> str:
    """
    Determine the database path from command line arguments or environment variables.
    Priority: command line argument > environment variable > default value
    """
    if args_db_path:
        return args_db_path
    
    env_db_path = os.getenv("MDLEX_DB_PATH")
    if env_db_path:
        return env_db_path
    
    return "mdlex.db"  # Default value if neither is set