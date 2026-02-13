import logging
import json
import os
import google.generativeai as genai

logger = logging.getLogger(__name__)

def load_ai_config():
    """Loads the AI configuration from the config file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('ai', {})
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def analyze_with_ai(target_data):
    """
    Sends collected target data to an external AI for analysis and attack suggestions.
    """
    ai_config = load_ai_config()
    api_key = ai_config.get("gemini_api_key")

    if not api_key:
        logger.warning("Gemini API key not found in config.json. Using placeholder analysis.")
        # Fallback to the old placeholder logic
        suggestions = []
        if any("GPSInfo" in key for key in target_data.get("metadata", [])):
            suggestions.append("[Placeholder] Target has GPS data. Recommend generating a phishing email related to a recently visited location.")
        if target_data.get("face_count", 0) > 0:
            suggestions.append(f"[Placeholder] Found {target_data['face_count']} unique faces. Recommend running facial recognition against known social media profiles.")
        if not suggestions:
            return ["[Placeholder] No specific high-value attack vectors identified."]
        return suggestions

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        As a security expert, analyze the following OSINT data collected for a target and suggest 3 creative, actionable attack vectors.
        For each suggestion, briefly explain your reasoning.

        Data:
        - Total unique faces identified: {target_data.get('face_count', 0)}
        - Metadata extracted from files: {target_data.get('metadata', [])}

        Suggestions:
        """

        response = model.generate_content(prompt)
        return response.text.strip().split('\n')

    except Exception as e:
        logger.error(f"An error occurred with the Gemini API: {e}")
        return ["An error occurred during AI analysis. Please check your API key and network connection."]
