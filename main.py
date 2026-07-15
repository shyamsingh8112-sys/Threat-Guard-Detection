from flask import Flask, render_template, request
import os
import google.generativeai as genai
import PyPDF2

app = Flask(__name__)

# Set up the google API
os.environ["Google_API_Key"] = "AIzaSyCPRyLnluYFn85ihXPoVccm7gg29rzePyg"
genai.configure(api_key=os.environ["Google_API_Key"])

# Initialize the gemini model
model = genai.GenerativeModel("gemini-2.5-flash")

# Prompt

def fake_pdf(text):
    prompt = f"""
    You are an expert id identifing scam message in text,email etc. Analyze the given text.

    - **Real/Lefitimate** (Authentic, Safe message)
    - **Scam/Fake** (Phishing, Fraud, Hacking etc.)

    ** for the following Text:**
    {text}

    ** Return a clear message indicating whether this is content is real or a scam.
    If it is a scam, mention why it seems fraudulent. If it is real, state that it is Legitimate.**

    ** Only return the classification message and nothing else.**
    Note: Don't return empty or null, you only need to return message for the input text.
    """

    response = model.generate_content(prompt)
    return response.text.strip() if response else "Classification failed."

def url_detection(url):
    prompt = f"""
    You are an advanced AI model specializing in URL security classification. Analyze the given URL and classify it as one of the following categories:

    1. Benign**: Safe, trusted, and non-malicious websites such as google.com, wikipedia.org, amazon.com.
    2. Phishing**: Fraudulent websites designed to steal personal information. Indicators include misspelled domains (e.g., paypa1.com instead of paypal.com), unusual subdomains, and misleading content.
    3. Malware**: URLs that distribute viruses, ransomware, or malicious software. Often includes automatic downloads or redirects to infected pages.
    4. Defacement**: Hacked or defaced websites that display unauthorized content, usually altered by attackers.

    *Example URLs and Classifications:*
    - *Benign*: "https://www.microsoft.com/"
    - *Phishing*: "http://secure-login.paypa1.com/"
    - *Malware*: "http://free-download-software.xyz/"
    - *Defacement*: "http://hacked-website.com/"

    *Input URL:* {url}

    *Output Format:*  
    - Return only a string class name
    - Example output for a phishing site:  

    Analyze the URL and return the correct classification (Only name in lowercase such as benign etc.)
    Note: Don't return empty or null, at any cost return the corrected class
    """

    response = model.generate_content(prompt)
    return response.text if response else "Detection failed."


# --------------------------------------------
# Simple Email Content Prediction Function Added
# --------------------------------------------
def predict_fake_or_real_email_content(text):
    # Simple logic for now (you can improve it later)
    if any(keyword in text.lower() for keyword in ["password", "login", "bank", "verify", "click here"]):
        return "Phishing content detected."
    else:
        return "Safe or benign content."


# Routes

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/scam/', methods=['POST'])
def detect_scam():
    if 'file' not in request.files:
        return render_template("index.html", message="No file uploaded.")

    file = request.files['file']
    extracted_text = ""

    if file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        extracted_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif file.filename.endswith('.txt'):
        extracted_text = file.read().decode("utf-8")
    else:
        return render_template("index.html", message="Invalid file type. Please upload a PDF or TXT file.")

    if not extracted_text.strip():
        return render_template("index.html", message="File is empty or text could not be extracted.")

    message = predict_fake_or_real_email_content(extracted_text)
    return render_template("index.html", message=message)


@app.route('/predict', methods=['POST'])
def predict_url():
    url = request.form.get('url', '').strip()

    if not url.startswith(("http://", "https://")):
        return render_template("index.html", message="Invalid URL format.", input_url=url)

    classification = url_detection(url)
    return render_template("index.html", input_url=url, predicted_class=classification)


if __name__ == '__main__':
    app.run(debug=True)
    
