import folium
import sqlite3
import logging
import os
import shutil
import ast
from .database import DB_FILE
from .ai_analyzer import analyze_with_ai

logger = logging.getLogger(__name__)

def generate_report(target_name, conn):
    """Generates a visual HTML report for a target."""
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM targets WHERE name = ?", (target_name,))
        target_row = cursor.fetchone()
        if not target_row:
            logger.error(f"Target '{target_name}' not found.")
            return

        target_id = target_row[0]

        # --- Report Directory ---
        report_dir = os.path.join("data", "reports", target_name)
        os.makedirs(report_dir, exist_ok=True)

        # --- Map Generation ---
        cursor.execute("""
            SELECT m.value FROM metadata m
            JOIN media ON m.media_id = media.id
            WHERE media.target_id = ? AND m.key = 'GPSInfo'
        """, (target_id,))

        locations = cursor.fetchall()

        m = folium.Map()
        has_locations = False
        if locations:
            for loc_str_tuple in locations:
                try:
                    # GPS data is stored as a string representation of a dict
                    gps_data = ast.literal_eval(loc_str_tuple[0])
                    if 'lat' in gps_data and 'lon' in gps_data:
                        lat = gps_data['lat']
                        lon = gps_data['lon']
                        folium.Marker([lat, lon], popup=f"Lat: {lat}, Lon: {lon}").add_to(m)
                        has_locations = True
                except (ValueError, SyntaxError) as e:
                    logger.warning(f"Could not parse GPS data '{loc_str_tuple[0]}': {e}")

        if has_locations:
             m.fit_bounds(m.get_bounds())

        map_path = os.path.join(report_dir, "map.html")
        m.save(map_path)

        # --- HTML Report Generation ---
        report_path = os.path.join(report_dir, "report.html")
        with open(report_path, "w") as f:
            f.write(f"<h1>OSINT Report for {target_name}</h1>")
            f.write("<h2>Interactive Map</h2>")
            f.write(f'<iframe src="map.html" width="100%" height="500px"></iframe>')

            # --- Face Gallery ---
            f.write("<h2>Face Gallery</h2>")
            faces_dir = os.path.join(report_dir, "faces")
            os.makedirs(faces_dir, exist_ok=True)

            cursor.execute("SELECT id FROM faces WHERE target_id = ?", (target_id,))
            faces = cursor.fetchall()
            if faces:
                for face in faces:
                    face_id = face[0]
                    f.write(f"<h3>Cluster {face_id}</h3>")
                    face_cluster_dir = os.path.join(faces_dir, str(face_id))
                    os.makedirs(face_cluster_dir, exist_ok=True)

                    cursor.execute("""
                        SELECT media.file_path FROM media
                        JOIN face_media ON media.id = face_media.media_id
                        WHERE face_media.face_id = ?
                    """, (face_id,))
                    images = cursor.fetchall()
                    for img_path_tuple in images:
                        img_path = img_path_tuple[0]
                        if os.path.exists(img_path):
                            shutil.copy(img_path, face_cluster_dir)
                            img_filename = os.path.basename(img_path)
                            f.write(f'<img src="faces/{face_id}/{img_filename}" width="150" style="margin:5px;">')
                        else:
                            logger.warning(f"Image file not found: {img_path}")
            else:
                f.write("<p>No faces processed for this target yet.</p>")

            # --- AI Suggestions ---
            f.write("<h2>AI-Powered Attack Suggestions</h2>")

            # Aggregate data for AI analysis
            target_data = {}
            cursor.execute("""
                SELECT m.key, m.value FROM metadata m
                JOIN media ON m.media_id = media.id
                WHERE media.target_id = ?
            """, (target_id,))
            metadata_rows = cursor.fetchall()
            target_data["metadata"] = [f"{key}: {value}" for key, value in metadata_rows]

            cursor.execute("SELECT COUNT(id) FROM faces WHERE target_id = ?", (target_id,))
            face_count = cursor.fetchone()[0]
            target_data["face_count"] = face_count

            suggestions = analyze_with_ai(target_data)

            if suggestions:
                f.write("<ul>")
                for s in suggestions:
                    f.write(f"<li>{s}</li>")
                f.write("</ul>")
            else:
                 f.write("<p>No AI suggestions could be generated. This might be due to a missing API key in config.json or insufficient data.</p>")


        logger.info(f"HTML report saved to {report_path}")

    except sqlite3.Error as e:
        logger.error(f"Database error during report generation: {e}")
