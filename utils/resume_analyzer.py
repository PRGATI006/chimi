"""Resume Analyzer - PDF Text Extraction & Skill Detection using PyPDF2"""

from PyPDF2 import PdfReader
import re

SKILL_KEYWORDS = {
    'programming': ['python', 'java', 'c++', 'javascript', 'sql', 'html', 'css'],
    'data': ['pandas', 'numpy', 'scikit-learn', 'tableau', 'sql', 'statistics'],
    'web': ['react', 'angular', 'node', 'django', 'flask', 'bootstrap'],
    'ai_ml': ['tensorflow', 'pytorch', 'machine learning', 'nlp', 'computer vision'],
    'cybersecurity': ['firewall', 'encryption', 'pentesting', 'ethical hacking', 'network']
}

def extract_text_from_pdf(file_path):
    """Extract text from PDF resume"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text.lower()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def analyze_resume_skills(resume_text):
    """Identify skills and categorize"""
    detected_skills = {}
    resume_lower = resume_text.lower()
    
    for category, keywords in SKILL_KEYWORDS.items():
        count = sum(1 for keyword in keywords if keyword in resume_lower)
        if count > 0:
            detected_skills[category] = count
    
    # Skill gap for popular careers
    gaps = {
        'software_engineer': len([k for k in SKILL_KEYWORDS['programming'] if k not in resume_lower]),
        'data_scientist': len([k for k in SKILL_KEYWORDS['data'] if k not in resume_lower]),
        'web_developer': len([k for k in SKILL_KEYWORDS['web'] if k not in resume_lower])
    }
    
    recommendations = []
    if gaps['software_engineer'] > 2:
        recommendations.append("Learn Python/Java and DSA")
    if gaps['data_scientist'] > 2:
        recommendations.append("Take Pandas/SQL courses")
    
    return detected_skills, gaps, recommendations

def generate_resume_score(resume_text):
    """Simple resume quality score"""
    score = 0
    if len(re.findall(r'\d{4}', resume_text)) > 0:  # Has dates
        score += 20
    if 'project' in resume_text:
        score += 30
    if 'experience' in resume_text or 'internship' in resume_text:
        score += 25
    if any(skill in resume_text for skill in ['python', 'sql', 'javascript']):
        score += 25
    
    return min(score, 100)


