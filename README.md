# AI-Powered Ingredient Safety Analyzer

This web application provides a personalized analysis of food and medicine ingredients. Users can upload an image of an ingredient list or paste the text directly to receive an instant safety report tailored to their individual health profile. The application uses OCR to extract text from images and Google's Gemini API for a comprehensive, AI-powered analysis.

## Features

- **User Authentication:** Secure user registration and login system.
- **Personalized Health Profiles:** Users can store their age, gender, dietary preferences, allergies, and medical conditions for a tailored analysis.
- **Dual Analysis Methods:** Supports both image upload (via OCR) and direct text input.
- **AI-Powered Analysis:** Leverages the Gemini API to provide a detailed safety report, including:
    - An overall safety score (0-100).
    - A "traffic light" indicator (Green, Yellow, Red).
    - A list of harmful ingredients with detailed descriptions.
    - Personalized recommendations and precautionary tips.
- **Modern, Responsive UI:** A clean and intuitive interface built with Bootstrap that works on both desktop and mobile devices.
- **Optimized Performance:** The entire analysis process is streamlined into a single, efficient API call.

## Getting Started

Follow these instructions to set up and run the application on your local machine.

### Prerequisites

- Python 3.7+
- Tesseract OCR
    - **Windows:** [Download and install from here](https://github.com/tesseract-ocr/tesseract). Make sure to add the installation directory to your system's PATH.
    - **macOS:** `brew install tesseract`
    - **Linux:** `sudo apt-get install tesseract-ocr`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-project-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    - Create a new file named `.env` in the root of your project directory.
    - Add your Google API key to this file as follows:
      ```
      GOOGLE_API_KEY='your_api_key_here'
      ```
    - You can obtain a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### Running the Application

1.  **Start the Flask server:**
    ```bash
    python run.py
    ```

2.  **Access the application:**
    - Open your web browser and navigate to `http://127.0.0.1:5000`.

## How to Use

1.  **Register and Log In:** Create an account and log in to get personalized results.
2.  **Update Your Profile:** Go to your profile page and fill in your health information.
3.  **Analyze a Product:**
    - **By Image:** Upload a clear picture of an ingredient list.
    - **By Text:** Copy and paste the ingredients into the text box.
4.  **View the Results:** The application will provide a detailed analysis, including a safety score, a list of harmful ingredients, and personalized recommendations.
