import os
import zipfile
import io
import stat
import logging

logger = logging.getLogger(__name__)

def create_polyglot(output_filename, files_to_zip, command_to_embed):
    """
    Creates a polyglot file that is both a shell script and a ZIP archive.
    """
    if not files_to_zip:
        logger.error("No files provided to zip for the polyglot.")
        return False

    # 1. Create the ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            if os.path.exists(file_path):
                zipf.write(file_path, os.path.basename(file_path))
            else:
                logger.warning(f"File not found, skipping: {file_path}")

    zip_data = zip_buffer.getvalue()

    # 2. Create the shell script header
    # The 'exec' redirects stdout and stderr to null to hide shell errors
    # from trying to execute the binary zip data. The final 'exit' is crucial.
    script_header = f"""#!/bin/bash
# This is a polyglot file (Shell Script + ZIP)
# The following command will be executed:
exec 1>/dev/null 2>&1
{command_to_embed}
exit 0
"""

    # 3. Combine the header and the zip data
    polyglot_content = script_header.encode('utf-8') + zip_data

    # 4. Write the polyglot file to disk
    try:
        with open(output_filename, 'wb') as f:
            f.write(polyglot_content)

        # 5. Make the file executable
        st = os.stat(output_filename)
        os.chmod(output_filename, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        logger.info(f"Polyglot file '{output_filename}' created successfully.")
        logger.info("It can be executed as a script or unzipped as an archive.")
        return True
    except IOError as e:
        logger.error(f"Failed to write polyglot file: {e}")
        return False
