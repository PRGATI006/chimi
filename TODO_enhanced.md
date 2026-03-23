# Enhanced Professional AI Career Guidance System - TODO

## Plan Breakdown:

**Information Gathered:**

- Current basic app running successfully (Flask-only, no deps issues).
- New specs: Modular structure (app.py, models/, utils/), advanced features (top 3 careers, resume PyPDF2, chatbot, personality test, Chart.js dashboard).
- Windows, no C compiler → Avoid scikit-learn build (use rule-based + simple pandas if wheel).
- Active terminals cleared.

**Files to Create/Update:**

1. requirements.txt → Flask, PyPDF2, pandas (wheels), no sklearn.
2. utils/career_engine.py → Top 3 careers, skill gap, roadmaps.
3. models/personality.py → MCQ test logic.
4. utils/chatbot.py → Predefined responses.
5. utils/resume_analyzer.py → PyPDF2 extraction.
6. templates/index.html → Add tabs (career form, personality test, resume upload).
7. templates/result.html → Top 3 cards, skill gap progress, Chart.js dashboard.
8. templates/chatbot.html → Simple chat UI.
9. static/script.js → AJAX chat, charts.
10. app.py → New routes (/predict, /chat, /upload, /personality).
11. uploads/ → For resume.
12. README.md → Updated instructions.

**Dependent Files:**

- All new except update app.py, templates/index.html, result.html, requirements.txt, README.md.

**Followup:**

- pip install new reqs.
- Test all features.
- Run app.py.

**Steps:**

- [x] Step 1: Update requirements.txt
- [x] Step 2: Create utils/ career_engine.py
- [x] Step 3: Create models/personality.py
- [x] Step 4: Create utils/chatbot.py
- [x] Step 5: Create utils/resume_analyzer.py
- [x] Step 6: Update app.py
- [ ] Step 7: Update templates/index.html, result.html
- [ ] Step 8: Create templates/chatbot.html
- [ ] Step 9: Update static/script.js, style.css
- [ ] Step 10: Update README.md
- [ ] Step 11: Create uploads/
- [ ] Step 12: Install & test
- [ ] Step 13: Complete

**Current Status:** Step 1 done. Starting Step 2.
