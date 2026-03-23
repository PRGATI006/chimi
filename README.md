# 🚀 AI Career Guidance System - Professional Edition

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/ai-career-guidance)](https://github.com/YOUR_USERNAME/ai-career-guidance)
[![License](https://img.shields.io/github/license/YOUR_USERNAME/ai-career-guidance)](https://github.com/YOUR_USERNAME/ai-career-guidance)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

**Advanced AI-powered career recommendation platform with resume analysis, personality testing, chatbot, and interactive charts.**

## ✨ Features

- **🎯 Top 3 Career Recommendations** with Chart.js dashboard
- **🧠 Dynamic Personality Test** (skills/domain-aware)
- **📄 Resume PDF Parser** (PyPDF2 - skills extraction)
- **💬 Real-time Career Chatbot** (AJAX)
- **📊 Skill Gap Analysis** + Personalized Roadmaps
- **📱 Fully Responsive** Bootstrap 5 + Custom CSS
- **🔧 Production Ready** (venv, requirements, error handling)
- **🛠️ Modular Architecture** (utils/, models/)

## 📁 Structure

```
.
├── app.py                 # Main Flask app
├── requirements.txt       # Dependencies
├── .gitignore            # Clean repo
├── README.md             # 📖 This!
├── templates/            # HTML pages
├── static/               # CSS/JS
├── utils/                # Business logic
├── models/               # ML models
├── uploads/              # Temp files (gitignored)
└── venv/                 # Virtual env (gitignored)
```

## 🚀 Quick Start (5 mins)

### Prerequisites

- Python 3.8+
- VS Code

### 1. Clone & Open

```bash
git clone https://github.com/YOUR_USERNAME/ai-career-guidance.git
cd ai-career-guidance
code .
```

### 2. Setup Environment

```
# Terminal (Ctrl+`)
python -m venv venv
venv\Scripts\activate   # Windows
# (venv) prompt appears

pip install -r requirements.txt
```

### 3. Run

```
python app.py
```

**Open:** http://127.0.0.1:5000

## 🎮 Demo Flow

1. **Career Assessment**: Skills → **Top 3 + Charts**
2. **Personality Test**: MCQ → Domain-fit career
3. **Resume Upload**: PDF → Skills score + gaps
4. **Chatbot**: "AI Engineer salary India?" → Answer

**Live Demo:** [Deployed Link](https://ai-career-guidance.onrender.com)

## 🛠️ Tech Stack

| Frontend    | Backend   | AI/ML      | Tools |
| ----------- | --------- | ---------- | ----- |
| Bootstrap 5 | Flask 3.0 | PyPDF2     | venv  |
| Chart.js    | Jinja2    | Rule-based | Git   |

## 🔍 Usage Examples

**Input:** `Python, ML | AI interests | B.Tech | AI domain`

```
Top Careers:
1. AI Engineer (92%)
2. Data Scientist (85%)
3. Software Engineer (78%)
```

## 📖 Contributing

1. Fork repo
2. `git checkout -b feature`
3. `git commit -m "Add feature"`
4. Push & PR

## 🤝 License

MIT - Free for commercial use!

## 👥 Contact

**Portfolio Ready!** Deploy, star, share 🚀

---

⭐ **Star this repo if helpful!**
