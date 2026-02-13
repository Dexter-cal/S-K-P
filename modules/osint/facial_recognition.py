import face_recognition
import sqlite3
import logging
from .database import DB_FILE

logger = logging.getLogger(__name__)

def process_faces(target_name, conn):
    """Processes all media for a target to find and cluster faces."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM targets WHERE name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            logger.error(f"Target '{target_name}' not found.")
            return

        target_id = target_row[0]

        cursor.execute("SELECT id, file_path FROM media WHERE target_id = ? AND type = 'image'", (target_id,))
        images = cursor.fetchall()

        known_face_encodings = []
        known_face_ids = []

        for media_id, file_path in images:
            try:
                image = face_recognition.load_image_file(file_path)
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)

                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                    face_id = -1
                    if True in matches:
                        first_match_index = matches.index(True)
                        face_id = known_face_ids[first_match_index]
                    else:
                        # This is a new face
                        cursor.execute("INSERT INTO faces (target_id) VALUES (?)", (target_id,))
                        face_id = cursor.lastrowid
                        known_face_encodings.append(face_encoding)
                        known_face_ids.append(face_id)

                    # Link the face to the media it appeared in
                    cursor.execute("INSERT INTO face_media (face_id, media_id) VALUES (?, ?)", (face_id, media_id))

            except Exception as e:
                logger.error(f"Could not process faces in {file_path}: {e}")

        conn.commit()
        logger.info(f"Facial recognition complete for target '{target_name}'.")

    except sqlite3.Error as e:
        logger.error(f"Database error during facial recognition: {e}")
