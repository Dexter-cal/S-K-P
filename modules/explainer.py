EXPLANATIONS = {
    "xxe": {
        "title": "XML External Entity (XXE)",
        "description": "An XXE attack is a type of attack against an application that parses XML input. It occurs when XML input containing a reference to an external entity is processed by a weakly configured XML parser.",
        "use_case": "Can be used to read local files on the server (e.g., /etc/passwd), perform Server-Side Request Forgery (SSRF) to scan the internal network, or cause a Denial of Service (DoS)."
    },
    "billion_laughs": {
        "title": "Billion Laughs Attack (XML Bomb)",
        "description": "A type of Denial of Service (DoS) attack that targets XML parsers. It consists of a nested entity expansion that grows exponentially, consuming a massive amount of memory and CPU.",
        "use_case": "Used to crash or hang web servers and applications that process XML, making them unavailable."
    },
    "zip_traversal": {
        "title": "ZIP Path Traversal (Zip Slip)",
        "description": "An archive-based vulnerability where an attacker crafts a ZIP file with file paths containing '..' (dot-dot-slash). When an insecure application extracts the archive, it can cause files to be overwritten outside of the intended directory.",
        "use_case": "Can be used to overwrite critical system files, plant a backdoor in a web root, or overwrite user profile scripts to gain code execution."
    },
    "csv_injection": {
        "title": "CSV Formula Injection",
        "description": "Occurs when a spreadsheet application (like Excel or Google Sheets) interprets a cell beginning with '=', '+', '-', or '@' as a formula. An attacker can embed malicious formulas in a CSV file.",
        "use_case": "Can be used to execute arbitrary commands on the user's computer (e.g., opening a calculator or a reverse shell) or to exfiltrate data from the spreadsheet via hyperlinks."
    },
    "pickle_deserialization": {
        "title": "Insecure Deserialization (Python Pickle)",
        "description": "Python's `pickle` module is not secure for deserializing data from untrusted sources. An attacker can craft a serialized object that, when deserialized, executes arbitrary code.",
        "use_case": "If an application deserializes user-provided data without validation, this can be used to gain a reverse shell or execute any command on the server."
    },
    "eicar": {
        "title": "EICAR Antivirus Test File",
        "description": "A standard, harmless string of text designed to test that antivirus software is working correctly. It is NOT a real virus.",
        "use_case": "Used to verify that an endpoint's antivirus or a server's file upload scanner is functioning. If the file is detected and blocked, the security control is working."
    }
}

def get_explanation(attack_type):
    """
    Returns a formatted explanation for a given attack type.
    """
    attack = EXPLANATIONS.get(attack_type.lower())
    if not attack:
        return f"No explanation found for '{attack_type}'. Available topics: {', '.join(EXPLANATIONS.keys())}"

    return f"""
--- {attack['title']} ---
Description: {attack['description']}
Use Case: {attack['use_case']}
--------------------
"""
