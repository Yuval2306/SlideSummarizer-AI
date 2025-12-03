"""
Database initialization script for Gemini Explainer.
This script creates the database tables and can be used to reset the database.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from database import create_tables, DB_FILE, engine


def init_database(force_recreate=False):
    """Initialize the database by creating all tables."""

    if force_recreate and os.path.exists(DB_FILE):
        print(f"Removing existing database file: {DB_FILE}")
        os.remove(DB_FILE)

    print(f"Creating database at: {DB_FILE}")
    create_tables()

    print("Database initialized successfully!")
    print(f"Tables created: users, uploads")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize the Gemini Explainer database")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate the database (deletes existing data)"
    )

    args = parser.parse_args()

    if args.force:
        response = input("This will delete all existing data. Are you sure? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)

    init_database(force_recreate=args.force)