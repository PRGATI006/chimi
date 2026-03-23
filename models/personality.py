"""Personality Test Model - Simple MCQ Scoring for Career Fit"""

PERSONALITY_QUESTIONS = [
    {
        "question": "How do you prefer to solve problems?",
        "options": ["Logically step-by-step", "Intuitively/creative", "Collaboratively", "Research/data-driven"],
        "scores": {"logical": 1, "creative": 2, "collaborative": 3, "data": 4}
    },
    {
        "question": "What interests you most in work?",
        "options": ["Building systems", "Analyzing data", "Designing UI", "Security/hacking", "Helping people"],
        "scores": {"build": 1, "analyze": 2, "design": 3, "security": 4, "help": 5}
    },
    # Add 8 more questions...
    {
        "question": "Your dream work environment?",
        "options": ["Solo coding", "Team brainstorming", "Remote freelance", "Office stable"],
        "scores": {"solo": 1, "team": 2, "remote": 3, "office": 4}
    }
]

CAREER_PERSONALITY_MAP = {
    0: "Software Engineer",  # Logical
    5: "Data Scientist",     # Analytical
    10: "Web Developer",     # Creative
    15: "AI Engineer",       # Tech advanced
    20: "Govt Jobs"          # Stable collaborative
}

def calculate_personality_score(answers):
    """Calculate score from MCQ answers"""
    score = 0
    for i, answer in enumerate(answers):
        # Simple scoring based on index
        score += (int(answer) + 1) * (i + 1)
    return score

def get_personality_career(score):
    """Map score to career suggestion"""
    for threshold, career in sorted(CAREER_PERSONALITY_MAP.items(), reverse=True):
        if score > threshold:
            return career
    return "Software Engineer"


