import argparse
import json
import sqlite3
from .core import init_db, load_docs, query_db, get_db_path

def handle_load_docs(args):
    """Handle the load_docs command"""
    db_path = get_db_path(args.db_path)
    conn = init_db(db_path, args.directory)
    try:
        docs_count = load_docs(conn, args.directory)
        print(f"Processed {docs_count} documents")
    finally:
        conn.close()

def handle_query_db(args):
    """Handle the query_db command"""
    db_path = get_db_path(args.db_path)
    conn = sqlite3.connect(db_path)

    try:
        results = query_db(conn, args.sql, tuple(args.params))
        print(json.dumps(results, indent=2))
    finally:
        conn.close()

def main():
    """Main function to parse arguments and execute commands"""
    parser = argparse.ArgumentParser(description="A utility for managing markdown documents with YAML frontmatter in SQLite.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for load_docs
    load_parser = subparsers.add_parser("load", help="Load markdown documents into the database")
    load_parser.add_argument("-db_path", help="Path to the SQLite database")
    load_parser.add_argument("directory", help="Directory containing markdown files")
    load_parser.set_defaults(func=handle_load_docs)

    # Subparser for query_db
    query_parser = subparsers.add_parser("query", help="Query the database")
    query_parser.add_argument("-db_path", help="Path to the SQLite database")
    query_parser.add_argument("sql", help="SQL query to execute")
    query_parser.add_argument("params", nargs="*", help="Parameters for the SQL query", default=[])
    query_parser.set_defaults(func=handle_query_db)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()