import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

DB_FILE = "data/osint_profiler.db"

def initialize_database():
    """Initializes the database and creates tables if they don't exist."""
    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # --- Targets Table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );
        """)

        # --- Media Table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                file_path TEXT NOT NULL,
                type TEXT,
                FOREIGN KEY (target_id) REFERENCES targets (id)
            );
        """)

        # --- Metadata Table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_id INTEGER,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                FOREIGN KEY (media_id) REFERENCES media (id)
            );
        """)

        conn.commit()
        logger.info("OSINT database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    initialize_database()
