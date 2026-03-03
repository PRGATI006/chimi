# AI-Based Certificate Fraud Detection System

A production-ready Flask web application that uses multiple AI models to detect fraudulent certificates:

- **DistilBERT** for text analysis
- **SSIM** for signature verification
- **OpenCV** for logo detection
- **Hough Circle Transform** for stamp verification

## Optimized for 8GB RAM Laptop (CPU Only)

## Features

- User registration and login
- Secure certificate upload (PDF, JPG, PNG)
- OCR text extraction
- Text fraud analysis using DistilBERT
- Signature detection using SSIM
- Logo detection using OpenCV template matching
- Digital stamp verification using Hough Circle
- Comprehensive fraud score calculation
- PDF and JSON report generation
- Admin dashboard for managing certificates

## Project Structure

```
certificate_fraud_detection/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models
├── forms.py               # WTForms
├── requirements.txt       # Python dependencies
├── README.md              # This file
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── result.html
│   └── admin.html
│
├── static/               # Static files
│   ├── uploads/          # Uploaded certificates
│   ├── logos/            # Reference logos
│   └── signatures/      # Reference signatures
│
├── ai_models/           # AI models
│   ├── nlp_model.py     # DistilBERT text analysis
│   ├── signature_check.py # SSIM signature detection
│   ├── logo_check.py    # OpenCV logo detection
│   └── stamp_check.py   # Hough Circle stamp verification
│
└── utils/               # Utilities
    ├── ocr.py           # OCR text extraction
    └── fraud_score.py   # Fraud score calculation
```

---

# INSTALLATION GUIDE

## Step 1: Install Python 3.10+

Download and install Python 3.10 or higher from https://www.python.org/

**Important:** During installation, check "Add Python to PATH"

## Step 2: Create Virtual Environment

Open terminal/command prompt and run:

```
bash
# Navigate to project directory
cd c:/Users/PRAGATI/PROJECT

# Create virtual environment
python -m venv venv
```

## Step 3: Activate Virtual Environment

**Windows:**

```
bash
# Activate virtual environment
venv\Scripts\activate
```

**macOS/Linux:**

```
bash
source venv/bin/activate
```

## Step 4: Upgrade pip

```
bash
pip install --upgrade pip
```

## Step 5: Install Dependencies

```
bash
pip install -r requirements.txt
```

## Step 6: Install Torch CPU Version

```
bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## Step 7: Install Tesseract OCR

### Windows:

1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Install to `C:\Program Files\Tesseract-OCR`
4. Add to PATH: `C:\Program Files\Tesseract-OCR`

### macOS:

```
bash
brew install tesseract
```

### Linux (Ubuntu):

```
bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

## Step 8: Run the Application

```
bash
python app.py
```

## Step 9: Open in Browser

Navigate to: http://127.0.0.1:5000

---

# DEFAULT CREDENTIALS

After running the app, use these credentials:

**Admin Account:**

- Email: admin@example.com
- Password: admin123

**Test User Account:**

- Email: user@example.com
- Password: user123

---

# HOW TO USE

1. **Register/Login**: Create an account or use test credentials
2. **Upload Certificate**: Go to Upload page and select a certificate (PDF, JPG, PNG)
3. **Wait for Analysis**: The system will:
   - Extract text using OCR
   - Run text analysis (DistilBERT)
   - Check signature using SSIM
   - Detect logo using OpenCV
   - Verify stamp using Hough Circle
4. **View Results**: See comprehensive fraud score and details
5. **Download Reports**: Export PDF or JSON reports

---

# TROUBLESHOOTING

## Tesseract Not Found

If you get Tesseract error:

- Install Tesseract as described in Step 7
- Or the app will use fallback text extraction

## CUDA/GPU Errors

The app is configured for CPU only. If you see CUDA errors:

- They are normal and will be handled automatically
- The app will fall back to CPU mode

## Out of Memory

If you have 8GB or less RAM:

- The app uses lightweight DistilBERT
- Image processing is optimized for CPU
- Should work without issues

## Database Errors

If you get database errors:

- Delete `database.db` if it exists
- Run `python app.py` again to recreate

---

# TECHNOLOGY STACK

- **Backend**: Flask 3.0
- **Database**: SQLite
- **Authentication**: Flask-Login
- **NLP**: DistilBERT (transformers)
- **Computer Vision**: OpenCV
- **Image Similarity**: scikit-image (SSIM)
- **OCR**: pytesseract
- **PDF**: reportlab

---

# LICENSE

MIT License

---

# CREDITS

- DistilBERT: Hugging Face
- OpenCV: Intel Corporation
- scikit-image: SciKit-Image Team
- Flask: Pallets
