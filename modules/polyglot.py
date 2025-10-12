import logging

def create_polyglot(image_path, zip_path, output_path):
    """
    Creates a polyglot file by combining an image and a ZIP file.
    The resulting file can be opened as both an image and a ZIP archive.
    """
    try:
        with open(image_path, 'rb') as f_image:
            image_data = f_image.read()

        with open(zip_path, 'rb') as f_zip:
            zip_data = f_zip.read()

        with open(output_path, 'wb') as f_polyglot:
            f_polyglot.write(image_data)
            f_polyglot.write(zip_data)

        logging.info(f"Polyglot file created at {output_path}")
        return True

    except Exception as e:
        logging.error(f"Error creating polyglot file: {e}")
        return False