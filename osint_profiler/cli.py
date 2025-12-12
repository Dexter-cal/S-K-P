import argparse
import logging
import sqlite3
from .database import initialize_database, DB_FILE
from .modules.media_processor import process_image, process_document
from .modules.attack_suggestor import suggest_attacks

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def handle_add_target(args):
    """Handles the 'add-target' command."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO targets (name, description) VALUES (?, ?)", (args.name, args.description))
        conn.commit()
        logger.info(f"Target '{args.name}' added successfully.")
    except sqlite3.IntegrityError:
        logger.error(f"Target '{args.name}' already exists.")
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def handle_add_media(args):
    """Handles the 'add-media' command."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM targets WHERE name = ?", (args.target,))
        target_row = cursor.fetchone()
        if not target_row:
            logger.error(f"Target '{args.target}' not found.")
            return

        target_id = target_row[0]

        # Determine file type and process
        file_type = "image" if args.path.lower().endswith(('.png', '.jpg', '.jpeg')) else "document"
        metadata = {}
        if file_type == "image":
            metadata = process_image(args.path)
        else:
            # Placeholder for document processing
            metadata = process_document(args.path)

        cursor.execute("INSERT INTO media (target_id, file_path, type) VALUES (?, ?, ?)",
                       (target_id, args.path, file_type))
        media_id = cursor.lastrowid

        for key, value in metadata.items():
            cursor.execute("INSERT INTO metadata (media_id, key, value) VALUES (?, ?, ?)",
                           (media_id, key, value))

        conn.commit()
        logger.info(f"Media '{args.path}' added to target '{args.target}' with {len(metadata)} metadata entries.")

    except sqlite3.Error as e:
        logger.error(f"Database error while adding media: {e}")
    finally:
        if conn:
            conn.close()

def main():
    """Main entry point for the CLI."""
    # Initialize the database at the start of the application
    initialize_database()

    parser = argparse.ArgumentParser(description="OSINT Profiler CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Add Target Command ---
    parser_add_target = subparsers.add_parser("add-target", help="Add a new target to the database.")
    parser_add_target.add_argument("name", help="The name of the target.")
    parser_add_target.add_argument("-d", "--description", help="A description of the target.")
    parser_add_target.set_defaults(func=handle_add_target)

    # --- Add Media Command ---
    parser_add_media = subparsers.add_parser("add-media", help="Add a media file to a target.")
    parser_add_media.add_argument("target", help="The name of the target.")
    parser_add_media.add_argument("path", help="The path to the media file.")
    parser_add_media.set_defaults(func=handle_add_media)

    # --- Suggest Attacks Command ---
    parser_suggest = subparsers.add_parser("suggest-attacks", help="Suggest attack vectors for a target.")
    parser_suggest.add_argument("target", help="The name of the target.")
    parser_suggest.set_defaults(func=lambda args: [print(f"  - {s}") for s in suggest_attacks(args.target)])

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
