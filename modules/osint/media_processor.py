from PIL import Image
from PIL.ExifTags import TAGS
import logging
from PyPDF2 import PdfFileReader
import json

logger = logging.getLogger(__name__)

def _convert_gps_to_decimal(gps_info):
    """Converts GPS exif data to decimal latitude and longitude."""
    def _convert_to_degrees(value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    try:
        lat_dms = gps_info.get(2)
        lat_ref = gps_info.get(1)
        lon_dms = gps_info.get(4)
        lon_ref = gps_info.get(3)

        if not all([lat_dms, lat_ref, lon_dms, lon_ref]):
            return None

        lat = _convert_to_degrees(lat_dms)
        if lat_ref in "S_":
            lat = -lat

        lon = _convert_to_degrees(lon_dms)
        if lon_ref in "W_":
            lon = -lon

        return {'lat': lat, 'lon': lon}
    except (IndexError, TypeError, ZeroDivisionError) as e:
        logger.warning(f"Could not parse GPS data: {gps_info}. Error: {e}")
        return None

def process_image(file_path):
    """Processes an image file to extract metadata."""
    metadata = {}
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)

                    if tag_name == "GPSInfo":
                        gps_coords = _convert_gps_to_decimal(value)
                        if gps_coords:
                            # Store as a JSON string for easy parsing later
                            metadata[str(tag_name)] = json.dumps(gps_coords)
                        continue # Move to next tag

                    # For other tags, convert to string safely
                    try:
                        metadata[str(tag_name)] = str(value)
                    except Exception:
                        # Some exif values can be complex objects
                        metadata[str(tag_name)] = repr(value)

                logger.info(f"Extracted {len(metadata)} EXIF tags from {file_path}")
    except Exception as e:
        logger.error(f"Could not process image {file_path}: {e}")

    return metadata

def process_document(file_path):
    """Processes a PDF document file to extract metadata."""
    metadata = {}
    try:
        with open(file_path, 'rb') as f:
            reader = PdfFileReader(f)
            doc_info = reader.getDocumentInfo()
            if doc_info:
                for key, value in doc_info.items():
                    # Key is like '/Title', so we clean it up
                    clean_key = key[1:]
                    metadata[clean_key] = str(value)
                logger.info(f"Extracted {len(metadata)} metadata fields from {file_path}")
    except Exception as e:
        logger.error(f"Could not process PDF {file_path}: {e}")

    return metadata
