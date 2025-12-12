import folium
import sqlite3
import logging
import os
from ..database import DB_FILE
from .ai_analyzer import analyze_with_ai

logger = logging.getLogger(__name__)

def generate_report(target_name):
    """Generates a visual HTML report for a target."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM targets WHERE name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            logger.error(f"Target '{target_name}' not found.")
            return

        target_id = target_row[0]

        # --- Map Generation ---
        # (This is a simplified example. A real implementation would parse GPS data more robustly)
        cursor.execute("""
            SELECT m.value FROM metadata m
            JOIN media ON m.media_id = media.id
            WHERE media.target_id = ? AND m.key LIKE '%GPS%'
        """, (target_id,))

        locations = cursor.fetchall()

        m = folium.Map()
        if locations:
            # Placeholder for actual GPS coordinate parsing
            # For now, just add a marker at a default location
            folium.Marker([40.7128, -74.0060], popup="Sample Location").add_to(m)

        map_path = f"data/{target_name}_map.html"
        m.save(map_path)
        logger.info(f"Map saved to {map_path}")

        # --- Data Aggregation for AI and Report ---
        target_data = {}
        cursor.execute("""
            SELECT m.key, m.value FROM metadata m
            JOIN media ON m.media_id = media.id
            WHERE media.target_id = ?
        """, (target_id,))
        target_data["metadata"] = cursor.fetchall()
        cursor.execute("SELECT COUNT(id) FROM faces WHERE target_id = ?", (target_id,))
        target_data["face_count"] = cursor.fetchone()[0]

        # --- HTML Report Generation ---
        report_path = f"data/{target_name}_report.html"
        with open(report_path, "w") as f:
            f.write(f"<h1>OSINT Report for {target_name}</h1>")
            f.write("<h2>Interactive Map</h2>")
            f.write(f'<iframe src="{os.path.basename(map_path)}" width="100%" height="500px"></iframe>')

            # --- Face Gallery ---
            f.write("<h2>Face Gallery</h2>")
            cursor.execute("SELECT id FROM faces WHERE target_id = ?", (target_id,))
            faces = cursor.fetchall()
            if faces:
                for face in faces:
                    face_id = face[0]
                    f.write(f"<h3>Cluster {face_id}</h3>")
                    cursor.execute("""
                        SELECT media.file_path FROM media
                        JOIN face_media ON media.id = face_media.media_id
                        WHERE face_media.face_id = ?
                    """, (face_id,))
                    images = cursor.fetchall()
                    for img_path in images:
                        # This assumes the media path is accessible from the report's location
                        f.write(f'<img src="{os.path.relpath(img_path[0], start="data")}" width="150" style="margin:5px;">')
            else:
                f.write("<p>No faces processed for this target yet.</p>")

            # --- AI Suggestions ---
            f.write("<h2>AI-Powered Attack Suggestions</h2>")
            suggestions = analyze_with_ai(target_data)
            f.write("<ul>")
            for s in suggestions:
                f.write(f"<li>{s}</li>")
            f.write("</ul>")


        logger.info(f"HTML report saved to {report_path}")

    except sqlite3.Error as e:
        logger.error(f"Database error during report generation: {e}")
    finally:
        if conn:
            conn.close()
