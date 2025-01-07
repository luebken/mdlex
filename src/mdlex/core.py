import sqlite3
import json
import yaml
import os
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, List
import re
import argparse

def init_db(db_path: str, directory: str) -> sqlite3.Connection:
    """Initialize SQLite database with schema-based views"""
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
    
    # Analyze schema and create views
    schema = analyze_frontmatter_schema(directory)
    
    # Print schema information
    print("\nFrontmatter Schema:")
    for prop, types in schema.items():
        type_names = [t.__name__ for t in types]
        print(f"  {prop}: {', '.join(type_names)}")
    
    # Check for schema consistency
    inconsistent_props = {prop: types for prop, types in schema.items() if len(types) > 1}
    if inconsistent_props:
        print("\nWarning: Inconsistent property types found:")
        for prop, types in inconsistent_props.items():
            type_names = [t.__name__ for t in types]
            print(f"  {prop}: {', '.join(type_names)}")
    
    # Create views based on schema
    create_schema_views(conn, schema)
    
    conn.commit()
    return conn

def create_schema_views(conn: sqlite3.Connection, schema: Dict[str, set]) -> None:
    """Create views for each property in the frontmatter schema"""
    cursor = conn.cursor()
    
    # First, drop any existing document_properties view
    cursor.execute("""
        DROP VIEW IF EXISTS document_properties
    """)
    
    # Create base view with id, filepath, content, and all frontmatter properties
    view_columns = ["id", "filepath", "content"]
    for prop_name in schema.keys():
        view_columns.append(f"json_extract(frontmatter, '$.{prop_name}') as {prop_name}")
    
    create_view_sql = f"""
        CREATE VIEW document_properties AS 
        SELECT 
            {', '.join(view_columns)}
        FROM documents
    """
    
    cursor.execute(create_view_sql)
    conn.commit()
    
def analyze_frontmatter_schema(directory: str) -> Dict[str, set]:
    """
    Analyze all markdown files to determine frontmatter schema.
    Returns a dictionary of property names and their value types.
    """
    schema = {}
    directory = Path(directory).resolve()

    for filepath in directory.rglob("*.md"):
        try:
            with filepath.open('r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, _ = extract_frontmatter(content)
            
            # For each property in the frontmatter
            for key, value in frontmatter.items():
                if key not in schema:
                    schema[key] = set()
                schema[key].add(type(value))

        except Exception as e:
            print(f"Error analyzing schema in {filepath}: {e}")
    
    return schema

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
    
    # Get column names from cursor description
    columns = [desc[0] for desc in cursor.description]
    
    # Convert rows to dictionaries using column names
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

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