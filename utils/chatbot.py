"""Simple Rule-Based Chatbot for Career Queries"""

CHAT_RESPONSES = {
    r'hello|hi|hey': "Hi! Ask me about careers, skills, or roadmaps. What's your interest?",
    r'software engineer': "Software Engineers earn ₹5-20LPA. Learn Python, DSA. Roadmap: LeetCode → Projects → Interviews.",
    r'data scientist': "Data Scientists average ₹8-25LPA. Skills: Python, ML, SQL. Start with Kaggle!",
    r'how to start coding': "1. Learn Python (freeCodeCamp). 2. Practice Codewars. 3. Build calculator app. Need help?",
    r'government jobs': "SSC CGL/ UPSC. Syllabus: Quant, Reasoning, English. Use Testbook app for mocks.",
    r'resume': "Upload your resume for skill analysis and improvements!",
    r'default': "Tell me your skills or interests for personalized career advice!"
}

def get_chat_response(user_message):
    """Get response based on keyword matching"""
    user_lower = user_message.lower()
    for pattern, response in CHAT_RESPONSES.items():
        import re
        if re.search(pattern, user_lower):
            return response
    return CHAT_RESPONSES['default']


