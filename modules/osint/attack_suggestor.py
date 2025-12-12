import sqlite3
import logging
from .database import DB_FILE

logger = logging.getLogger(__name__)

def suggest_attacks(target_name):
    """Analyzes collected data for a target and suggests attack vectors."""
    suggestions = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM targets WHERE name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            logger.error(f"Target '{target_name}' not found.")
            return []

        target_id = target_row[0]

        # Suggestion based on GPS data in images
        cursor.execute("""
            SELECT m.value FROM metadata m
            JOIN media ON m.media_id = media.id
            WHERE media.target_id = ? AND m.key = 'GPSInfo'
        """, (target_id,))

        if cursor.fetchone():
            suggestions.append("Found GPS data in images. Consider physical security testing or social engineering based on location patterns.")

    except sqlite3.Error as e:
        logger.error(f"Database error during attack suggestion: {e}")
    finally:
        if conn:
            conn.close()

    return suggestions
