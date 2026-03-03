# 🎓 AI-Based Certificate Fraud Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

> 🔒 An intelligent certificate authentication system that uses multiple AI models to detect fraudulent certificates with high accuracy.

## 📋 Table of Contents

- [Overview](#overview)
- [✨ Features](#features)
- [🛠️ Technologies Used](#technologies-used)
- [📁 Project Structure](#project-structure)
- [🚀 Getting Started](#getting-started)
- [📸 Screenshots](#screenshots)
- [🔬 How It Works](#how-it-works)
- [🎯 Future Improvements](#future-improvements)
- [📄 License](#license)
- [👤 Author](#author)

---

## 📖 Overview

The **AI-Based Certificate Fraud Detection System** is a production-ready Flask web application designed to identify fraudulent certificates using multiple artificial intelligence techniques. This project addresses the critical need for automated certificate verification in educational institutions, HR departments, and organizations that rely on credential validation.

The system employs a multi-layered approach combining:

- **Natural Language Processing (NLP)** for text analysis
- **Computer Vision** for signature, logo, and stamp verification
- **Machine Learning** for fraud scoring

### 🎯 Problem Statement

Certificate fraud is a growing concern in academic and professional circles. Manual verification is time-consuming and prone to errors. This project provides an automated, scalable solution that can analyze certificates within seconds.

---

## ✨ Features

### 🔐 Authentication & User Management

- User registration and secure login
- Role-based access (Regular User / Admin)
- Session management with Flask-Login

### 📤 Certificate Upload & Processing

- Support for multiple file formats (PDF, JPG, PNG)
- Secure file storage with unique filenames
- Automatic OCR text extraction

### 🤖 AI-Powered Analysis

| Feature                    | Technology                   | Description                                   |
| -------------------------- | ---------------------------- | --------------------------------------------- |
| **Text Analysis**          | DistilBERT                   | NLP-based fraud detection in certificate text |
| **Signature Verification** | SSIM (Structural Similarity) | Detects signature tampering and forgeries     |
| **Logo Detection**         | OpenCV Template Matching     | Identifies counterfeit organizational logos   |
| **Stamp Verification**     | Hough Circle Transform       | Verifies authenticity of digital stamps       |

### 📊 Results & Reporting

- Comprehensive fraud score calculation (0-100%)
- Detailed breakdown of each analysis component
- PDF and JSON report generation
- Visual indicators for suspicious certificates

### 👨‍💼 Admin Dashboard

- View all uploaded certificates
- Filter by suspicious/verified status
- Toggle suspicious flags
- System statistics and analytics

---

## 🛠️ Technologies Used

### Backend & Server

<p>
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/WTForms-FF6F00?style=flat" alt="WTForms">
</p>

### AI & Machine Learning

<p>
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch" alt="PyTorch">
  <img src="https://img.shields.io/badge/Transformers-FF9A00?style=flat&logo=huggingface" alt="Transformers">
  <img src="https://img.shields.io/badge/DistilBERT-FF9A00?style=flat&logo=huggingface" alt="DistilBERT">
</p>

### Computer Vision

<p>
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv" alt="OpenCV">
  <img src="https://img.shields.io/badge/scikit--image-FF6F00?style=flat" alt="scikit-image">
  <img src="https://img.shields.io/badge/Pillow-ECECEC?style=flat&logo=pillow" alt="Pillow">
</p>

### OCR & Document Processing

<p>
  <img src="https://img.shields.io/badge/Tesseract%20OCR-5C3EE8?style=flat" alt="Tesseract">
  <img src="https://img.shields.io/badge/pytesseract-FF6F00?style=flat" alt="pytesseract">
  <img src="https://img.shields.io/badge/ReportLab-0066CC?style=flat" alt="ReportLab">
</p>

### Additional Tools

- **Python 3.10+** - Programming Language
- **Werkzeug** - Security & Password Hashing
- **HTML/CSS/JavaScript** - Frontend

---

## 📁 Project Structure

```
certificate-fraud-detection/
│
├── 📄 Core Files
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── models.py              # Database models (User, Certificate)
│   ├── forms.py               # WTForms for validation
│   ├── requirements.txt       # Python dependencies
│   └── README.md              # Project documentation
│
├── 📂 templates/               # HTML templates
│   ├── base.html              # Base template
│   ├── index.html             # Landing page
│   ├── login.html             # Login form
│   ├── register.html          # Registration form
│   ├── dashboard.html         # User dashboard
│   ├── upload.html            # Certificate upload
│   ├── result.html            # Analysis results
│   └── admin.html             # Admin dashboard
│
├── 📂 static/                 # Static assets
│   ├── uploads/               # Uploaded certificates
│   ├── logos/                 # Reference logos
│   ├── signatures/            # Reference signatures
│   └── css/                   # Stylesheets
│
├── 🤖 ai_models/              # AI detection models
│   ├── nlp_model.py           # DistilBERT text analysis
│   ├── signature_check.py     # SSIM signature detection
│   ├── logo_check.py          # OpenCV logo detection
│   └── stamp_check.py         # Hough Circle stamp verification
│
└── 🔧 utils/                  # Utility functions
    ├── ocr.py                 # Text extraction
    └── fraud_score.py         # Fraud score calculation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- 4GB+ RAM (8GB recommended for AI models)
- Tesseract OCR installed

### Installation Steps

#### 1️⃣ Clone the Repository

```
bash
git clone https://github.com/PRGATI006/chimi.git
cd certificate-fraud-detection
```

#### 2️⃣ Create Virtual Environment

```
bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies

```
bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4️⃣ Install PyTorch (CPU Version)

```
bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 5️⃣ Install Tesseract OCR

**Windows:**

- Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Install to `C:\Program Files\Tesseract-OCR`
- Add to PATH

**macOS:**

```
bash
brew install tesseract
```

**Linux (Ubuntu):**

```
bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### 6️⃣ Run the Application

```
bash
python app.py
```

#### 7️⃣ Access the Application

Open your browser and navigate to: **http://127.0.0.1:5000**

---

### 🔑 Default Credentials

After first run, use these credentials:

| Role          | Email             | Password |
| ------------- | ----------------- | -------- |
| **Admin**     | admin@example.com | admin123 |
| **Test User** | user@example.com  | user123  |

---

## 📸 Screenshots

### 🏠 Landing Page

![Landing Page](https://via.placeholder.com/800x400?text=Landing+Page+Screenshot)

### 🔐 Login Page

![Login Page](https://via.placeholder.com/800x400?text=Login+Page+Screenshot)

### 📤 Upload Certificate

![Upload Page](https://via.placeholder.com/800x400?text=Certificate+Upload+Screenshot)

### 📊 Results Dashboard

![Results](https://via.placeholder.com/800x400?text=Analysis+Results+Screenshot)

### 👨‍💼 Admin Panel

![Admin Panel](https://via.placeholder.com/800x400?text=Admin+Dashboard+Screenshot)

---

## 🔬 How It Works

### Flow Diagram

```
┌─────────────────┐
│  User Uploads  │
│   Certificate  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  OCR Extraction │
│   (pytesseract)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│           PARALLEL AI ANALYSIS               │
├─────────────┬─────────────┬─────────────────┤
│  DistilBERT │     SSIM    │   OpenCV        │
│  Text Fraud │  Signature  │ Logo & Stamp    │
│  Detection  │  Detection  │   Detection     │
└─────────────┴─────────────┴─────────────────┘
         │
         ▼
┌─────────────────┐
│  Fraud Score    │
│  Calculation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Generate Report│
│  (PDF/JSON)     │
└─────────────────┘
```

### Fraud Score Algorithm

The overall fraud score is calculated using a weighted average:

```
Overall Score = (Text Score × 0.30) + (Signature Score × 0.25) +
                (Logo Score × 0.25) + (Stamp Score × 0.20)
```

- **Score > 50%**: Flagged as suspicious
- **Score < 50%**: Considered legitimate

---

## 🎯 Future Improvements

### Short-term Goals

- [ ] Implement blockchain-based certificate verification
- [ ] Add batch processing for multiple certificates
- [ ] Improve OCR accuracy with custom training
- [ ] Add multi-language support

### Long-term Goals

- [ ] Deploy as a REST API for integration
- [ ] Implement real-time certificate validation
- [ ] Add mobile application support
- [ ] Integrate with popular HR platforms
- [ ] Use ensemble learning for better accuracy
- [ ] Implement blockchain ledger for immutable records

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

<div align="center">
  <img src="https://via.placeholder.com/150x150?text=Your+Photo" alt="Profile" style="border-radius: 50%;">
  
  **Your Name**
  
  🎓 Computer Science Student | 🤖 AI/ML Enthusiast | 🌐 Web Developer
  
  <p>
    <a href="https://linkedin.com/in/YOUR_LINKEDIN">
      <img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin" alt="LinkedIn">
    </a>
    <a href="https://github.com/PRGATI006">
      <img src="https://img.shields.io/badge/GitHub-333333?style=flat&logo=github" alt="GitHub">
    </a>
    <a href="mailto:your.email@example.com">
      <img src="https://img.shields.io/badge/Email-D14836?style=flat&logo=gmail" alt="Email">
    </a>
  </p>
</div>

---

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) - DistilBERT model
- [OpenCV](https://opencv.org/) - Computer vision library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [scikit-image](https://scikit-image.org/) - Image processing

---

<div align="center">
  ⭐ Star this repository if you found it helpful!
  
  Made with ❤️ for a fraud-free world
</div>
