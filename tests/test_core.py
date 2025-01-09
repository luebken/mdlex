import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
import pytest
from mdlex.core import (
    init_db,
    extract_frontmatter,
    load_docs,
    query_db,
    get_db_path,
    serialize_dates,
    analyze_frontmatter_schema,
    create_schema_views
)

@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database"""
    db_path = tmp_path / "test.db"
    return str(db_path)

@pytest.fixture
def sample_docs(tmp_path):
    """Create sample markdown documents"""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    
    # Create test document 1
    doc1 = docs_dir / "test1.md"
    doc1.write_text("""---
title: Test Document 1
date: 2023-01-01
tags:
  - test
  - markdown
---
# Test Content 1
This is a test document.""")

    # Create test document 2
    doc2 = docs_dir / "test2.md"
    doc2.write_text("""---
title: Test Document 2
date: 2023-01-02
count: 42
---
# Test Content 2
Another test document.""")
    
    return str(docs_dir)

def test_extract_frontmatter():
    """Test YAML frontmatter extraction"""
    content = """---
title: Test
date: 2023-01-01
---
# Content
Test content."""
    
    frontmatter, content = extract_frontmatter(content)
    assert frontmatter == {"title": "Test", "date": date(2023, 1, 1)}
    assert content.strip() == "# Content\nTest content."

def test_extract_frontmatter_no_yaml():
    """Test handling content without frontmatter"""
    content = "# Just Content\nNo frontmatter here."
    frontmatter, content = extract_frontmatter(content)
    assert frontmatter == {}
    assert content == "# Just Content\nNo frontmatter here."

def test_serialize_dates():
    """Test date serialization"""
    test_date = date(2023, 1, 1)
    test_datetime = datetime(2023, 1, 1, 12, 0)
    
    assert serialize_dates(test_date) == "2023-01-01"
    assert serialize_dates(test_datetime) == "2023-01-01T12:00:00"
    
    with pytest.raises(TypeError):
        serialize_dates("not a date")

def test_get_db_path():
    """Test database path resolution"""
    assert get_db_path(None) == "mdlex.db"
    assert get_db_path("custom.db") == "custom.db"
    
    # Test with environment variable
    os.environ["MDLEX_DB_PATH"] = "env.db"
    assert get_db_path(None) == "env.db"
    del os.environ["MDLEX_DB_PATH"]

def test_analyze_frontmatter_schema(sample_docs):
    """Test frontmatter schema analysis"""
    schema = analyze_frontmatter_schema(sample_docs)
    
    assert "title" in schema
    assert str in schema["title"]
    assert "date" in schema
    assert date in schema["date"]
    assert "tags" in schema
    assert list in schema["tags"]
    assert "count" in schema
    assert int in schema["count"]

def test_database_operations(temp_db, sample_docs):
    """Test database initialization and document loading"""
    # Initialize database
    conn = init_db(temp_db, sample_docs)
    
    # Load documents
    docs_count = load_docs(conn, sample_docs)
    assert docs_count == 2
    
    # Query documents
    results = query_db(conn, "SELECT * FROM documents")
    assert len(results) == 2
    
    # Verify document content
    assert any(doc["title"] == "Test Document 1" for doc in results)
    assert any(doc["title"] == "Test Document 2" for doc in results)
    
    # Test specific document queries
    test_doc = query_db(conn, "SELECT * FROM documents WHERE title = ?", ("Test Document 1",))
    assert len(test_doc) == 1
    assert test_doc[0]["title"] == "Test Document 1"
    
    conn.close()