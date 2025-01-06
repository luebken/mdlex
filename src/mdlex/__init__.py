"""
mdlex - A utility for managing markdown documents with YAML frontmatter in SQLite
"""

from .core import (
    init_db,
    extract_frontmatter,
    load_docs,
    query_db,
    get_db_path,
)

__version__ = "0.1.0"