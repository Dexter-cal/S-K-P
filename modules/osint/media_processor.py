from PIL import Image
from PIL.ExifTags import TAGS
import logging

logger = logging.getLogger(__name__)

def process_image(file_path):
    """Processes an image file to extract metadata."""
    metadata = {}
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    metadata[str(tag_name)] = str(value)
                logger.info(f"Extracted {len(metadata)} EXIF tags from {file_path}")
    except Exception as e:
        logger.error(f"Could not process image {file_path}: {e}")

    return metadata

def process_document(file_path):
    """Processes a PDF document file to extract metadata."""
    metadata = {}
    try:
        from PyPDF2 import PdfFileReader
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
