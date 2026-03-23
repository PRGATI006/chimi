# 🚀 GitHub Upload Guide - Step by Step Commands

Follow these commands to upload your project to GitHub professionally.

---

## 📋 Step 1: Check Git Installation

First, verify that Git is installed on your system:

```
bash
git --version
```

If Git is not installed, download it from: https://git-scm.com/

---

## 📂 Step 2: Navigate to Your Project

```
bash
cd c:/Users/PRAGATI/PROJECT
```

---

## 🔧 Step 3: Configure Git (If First Time)

```
bash
# Set your name
git config --global user.name "Your Name"

# Set your email
git config --global user.email "your.email@example.com"
```

---

## 📦 Step 4: Initialize Git Repository

```
bash
git init
```

---

## 📝 Step 5: Create .gitignore File

Create a `.gitignore` file to exclude unnecessary files:

```
bash
# Create .gitignore file
```

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite
instance/

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Uploads (optional - keep if you want sample files)
static/uploads/
```

---

## ➕ Step 6: Add Files to Staging

### Add all files:

```
bash
git add .
```

### Or add specific files/folders:

```
bash
git add app.py
git add config.py
git add models.py
git add forms.py
git add requirements.txt
git add templates/
git add static/
git add ai_models/
git add utils/
```

### Check status:

```
bash
git status
```

---

## 💾 Step 7: Commit Your Project

```
bash
git commit -m "Initial commit: AI-Based Certificate Fraud Detection System

Features:
- DistilBERT for text analysis
- SSIM for signature verification
- OpenCV for logo detection
- Hough Circle for stamp verification
- User authentication
- Admin dashboard
- PDF/JSON report generation"
```

---

## 🔗 Step 8: Create GitHub Repository

### Option A: Using GitHub CLI (Recommended)

First, install GitHub CLI if not already installed:

**Windows:**

```
winget install GitHub.cli
```

OR download from: https://github.com/cli/cli/releases

Then:

```
bash
# Check if gh is installed
gh --version

# Login to GitHub
gh auth login
# (Follow the prompts: HTTPS, Login with web browser, copy the one-time code)

# Create repository
gh repo create certificate-fraud-detection --public --source=. --description "AI-Based Certificate Fraud Detection System using DistilBERT, OpenCV, and Computer Vision"

# Push to GitHub
git push -u origin main
```

### Option B: Using Git Commands (Browser Method)

1. Go to: https://github.com/new
2. Repository name: `certificate-fraud-detection`
3. Description: `AI-Based Certificate Fraud Detection System using DistilBERT, OpenCV, and Computer Vision`
4. Select: **Public**
5. Click: **Create repository**
6. Copy the commands shown and run them:

```
bash
# Run these commands (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/certificate-fraud-detection.git
git branch -M main
git push -u origin main
```

---

## 🔄 Step 9: Verify Upload

```
bash
# Check remote
git remote -v

# View commit history
git log
```

---

## 📤 Additional Commands

### Add changes later:

```
bash
# Check changes
git status

# Add modified files
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push
```

### Create a new branch:

```bash
git checkout -b feature-name
git push -u origin feature-name
```

### Pull latest changes:

```
bash
git pull origin main
```

---

## ✅ Quick Reference

```
bash
# Complete workflow for future updates
git add .
git commit -m "Your message"
git push
```

---

## 🎯 After Uploading

1. Add topics/tags to your repository
2. Add README.md (the professional one we created)
3. Add license (MIT recommended)
4. Create a release version
5. Share on LinkedIn!

---

## 📞 Troubleshooting

### If you get authentication error:

```
bash
# Set up GitHub Personal Access Token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/certificate-fraud-detection.git
```

### If origin already exists:

```
bash
git remote rm origin
git remote add origin https://github.com/YOUR_USERNAME/certificate-fraud-detection.git
```

---

**Note:** Replace `YOUR_USERNAME` and `Your Name` with your actual GitHub username and name.
