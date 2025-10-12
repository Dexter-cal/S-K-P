import os
import logging

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
AUDIO_EXTENSIONS = ['.wav']

VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov']

def discover_files(file_type, search_path='.'):
    """
    Discovers files of a specific type in a given search path.

    :param file_type: The type of file to discover ('image', 'audio', or 'video').
    :param search_path: The directory to search in.
    :return: A list of file paths.
    """
    found_files = []
    if file_type == 'image':
        extensions = IMAGE_EXTENSIONS
    elif file_type == 'audio':
        extensions = AUDIO_EXTENSIONS
    elif file_type == 'video':
        extensions = VIDEO_EXTENSIONS
    else:
        logging.error(f"Unsupported file type for discovery: {file_type}")
        return found_files

    logging.info(f"Searching for {file_type} files in {os.path.abspath(search_path)}...")
    for root, _, files in os.walk(search_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                found_files.append(os.path.join(root, file))

    logging.info(f"Found {len(found_files)} {file_type} files.")
    return found_files