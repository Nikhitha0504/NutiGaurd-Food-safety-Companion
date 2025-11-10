import os
import json
import re
import google.generativeai as genai
from PIL import Image
import pytesseract
import shutil
from dotenv import load_dotenv
import cv2

# Load environment variables
load_dotenv()

# --- Gemini Client Initialization ---
try:
    API_KEY = os.getenv('GOOGLE_API_KEY')
    if not API_KEY:
        print("🔥 WARNING: GOOGLE_API_KEY is not set in the .env file.")
        model = None
    else:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Google GenAI Client initialized successfully.")
except Exception as e:
    print(f"🔥 FAILED to initialize Google GenAI Client: {e}")
    model = None

# --- Tesseract Configuration ---
# Uncomment and set the path if Tesseract is not in your system's PATH
# For Windows:
tesseract_path = os.getenv('TESSERACT_PATH')
if tesseract_path and os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    # If not in PATH, try the default Windows installation path
    if not shutil.which('tesseract'):
        default_path = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        if os.path.exists(default_path):
            pytesseract.pytesseract.tesseract_cmd = default_path

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Preprocess image for better OCR results"""
    try:
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        return enhanced
    except Exception as e:
        print(f"Preprocessing error: {str(e)}")
        return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

def extract_text_from_image(image_path):
    """Extract text from image using OCR (Tesseract)"""
    try:
        preprocessed = preprocess_image(image_path)
        pil_image = Image.fromarray(preprocessed)
        custom_config = r'--oem 3 --psm 6'
        extracted_text = pytesseract.image_to_string(pil_image, config=custom_config)
        if not extracted_text.strip():
            custom_config = r'--oem 3 --psm 11'
            extracted_text = pytesseract.image_to_string(pil_image, config=custom_config)
        return extracted_text
    except Exception as e:
        return f"OCR Error: {str(e)}"

def get_full_analysis_from_text(text, user_profile=None):
    """Extracts ingredients and analyzes them in a single Gemini API call."""
    if not model:
        return json.dumps({"error": "Gemini client not initialized. Check API key."})

    profile_lines = []
    if isinstance(user_profile, dict):
        for key in [
            'name', 'age', 'gender', 'height', 'weight',
            'dietary_preferences', 'allergies', 'medical_conditions', 'lifestyle_habits'
        ]:
            val = user_profile.get(key)
            if val is not None and str(val).strip():
                profile_lines.append(f"- {key.replace('_', ' ').title()}: {val}")
    profile_text = "\n".join(profile_lines)
    profile_block = f"\n\nUSER PROFILE:\n{profile_text}" if profile_text else ""

    prompt = f"""You are an expert nutrition and health analyst. Below is text from a product label.

PRODUCT LABEL TEXT:
{text}
{profile_block}

Perform two tasks:
1.  **Extraction**: Identify the product name and all ingredients from the text.
2.  **Analysis**: Provide a full health and safety analysis of the identified ingredients, personalized for the user's health profile.

Return a SINGLE JSON object with this EXACT format:
{{
    "extraction": {{
        "product_name": "The exact product name",
        "ingredients": ["ingredient1", "ingredient2", "..."],
        "product_type": "food/medicine/supplement/beverage/other"
    }},
    "analysis": {{
        "overall_safety_score": <number from 0-100>,
        "traffic_light": "Green/Yellow/Red",
        "summary": "A brief, personalized summary of the analysis.",
        "harmful_ingredients": [
            {{
                "ingredient": "ingredient_name",
                "reason": "Why it's harmful, especially for the user.",
                "description": "A brief explanation of what this ingredient is.",
                "identification": "How to spot this ingredient on labels (e.g., other names)."
            }}
        ],
        "recommendations": "Suggest 2–3 healthier alternatives of the same product type (e.g., if chocolate → dark or sugar-free chocolate; if chips → baked or multigrain chips) with a short reason for why each is healthier.","
        ],
        
        "precautionary_tips": [
            "What to do if you've already consumed the product (e.g., 'Stay hydrated')."
        ]
    }}
}}

Rules:
- If no ingredients are found, return an empty list for "ingredients".
- The safety score must be an integer from 0 to 100.
- The traffic light is Green (>=80), Yellow (50-79), or Red (<50).
- Personalize the analysis based on the user's full profile (age, gender, conditions, allergies, lifestyle, etc.).
- Provide detailed, actionable information for the 'description', 'identification', and 'precautionary_tips' fields.
- Return ONLY the JSON object and nothing else."""

    try:
        response = model.generate_content(
            contents=prompt
        )
        return response.text
    except Exception as e:
        return json.dumps({"error": f"Gemini API error: {str(e)}"})

def parse_json_response(response_text):
    """Extract and parse JSON from response text"""
    try:
        # Find the JSON block in the response text
        json_str = response_text.strip().replace('```json', '').replace('```', '')
        return json.loads(json_str)
    except json.JSONDecodeError:
        print(f"JSON Decode Error. Raw response:\n{response_text}")
        return {"error": "Failed to parse AI response. The response was not valid JSON."}
    except Exception as e:
        return {"error": f"An unexpected error occurred while parsing the response: {str(e)}"}
