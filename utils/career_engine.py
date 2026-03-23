"""Career Recommendation Engine - Top 3 Careers, Skill Gap Analysis, Roadmaps"""

CAREERS = {
    'software_engineer': {
        'required_skills': ['python', 'java', 'c++', 'programming', 'algorithms', 'data structures', 'sql'],
        'roadmap': ['Learn Python/Java', 'DSA LeetCode', 'Build projects', 'GitHub portfolio', 'System design', 'Apply jobs'],
        'demand': 95
    },
    'data_scientist': {
        'required_skills': ['statistics', 'python', 'pandas', 'sql', 'machine learning', 'matplotlib'],
        'roadmap': ['Python + Pandas', 'Statistics/SQL', 'ML Scikit-learn', 'Kaggle competitions', 'Tableau/PowerBI', 'Data roles'],
        'demand': 88
    },
    'web_developer': {
        'required_skills': ['html', 'css', 'javascript', 'react', 'node', 'bootstrap'],
        'roadmap': ['HTML/CSS/JS', 'React/Vue', 'Backend Node/Flask', 'Deploy Heroku', 'Freelance Upwork', 'Fullstack jobs'],
        'demand': 92
    },
    'ai_engineer': {
        'required_skills': ['python', 'tensorflow', 'pytorch', 'ml', 'nlp', 'computer vision'],
        'roadmap': ['Python ML', 'Deep Learning', 'Projects chatbot/CV', 'Paperswithcode', 'Cloud AWS', 'AI startups'],
        'demand': 97
    },
    'cybersecurity': {
        'required_skills': ['networking', 'linux', 'ethical hacking', 'firewall', 'encryption', 'pentesting'],
        'roadmap': ['Networking basics', 'Linux commands', 'CEH certification', 'TryHackMe', 'CTF competitions', 'Security analyst'],
        'demand': 85
    },
    'govt_jobs': {
        'required_skills': ['reasoning', 'quantitative', 'english', 'gk', 'current affairs'],
        'roadmap': ['SSC syllabus', 'Daily newspaper', 'Mock tests', 'Testbook/Gradeup', 'UPSC/SSC exams'],
        'demand': 80
    }
}

def get_top_careers(skills, interests, education, domain):
    """Return top 3 careers with scores"""
    skills_lower = skills.lower()
    interests_lower = interests.lower()
    
    scores = {}
    for career, data in CAREERS.items():
        score = 0.0
        # Skills match
        skill_match = sum(1 for skill in data['required_skills'] if skill in skills_lower)
        score += skill_match * 10
        
        # Interests match
        if any(word in interests_lower for word in data['required_skills'][:3]):
            score += 20
            
        # Domain match (simple)
        if domain.lower() in career:
            score += 15
            
        scores[career] = score * data['demand'] / 100
    
    # Top 3
    top_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return top_careers

def skill_gap_analysis(user_skills, career):
    """Calculate skill match % and missing skills"""
    data = CAREERS[career]
    required = data['required_skills']
    user_lower = set(user_skills.lower().split(','))
    
    matched = sum(1 for skill in required if skill in user_lower)
    match_pct = (matched / len(required)) * 100
    
    missing = [skill for skill in required if skill not in user_lower]
    
    return match_pct, missing, data['roadmap']

def get_career_roadmap(career):
    """Get detailed roadmap"""
    return CAREERS[career]['roadmap']

