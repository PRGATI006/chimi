from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from utils.career_engine import get_top_careers, skill_gap_analysis
from utils.chatbot import get_chat_response
from utils.resume_analyzer import extract_text_from_pdf, analyze_resume_skills, generate_resume_score
from models.personality import calculate_personality_score, get_personality_career

app = Flask(__name__)
app.secret_key = 'professional_ai_career_secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    skills = request.form.get('skills', '').strip()
    interests = request.form.get('interests', '').strip()
    education = request.form.get('education', '').strip()
    domain = request.form.get('domain', '').strip()
    
    if not all([skills, interests, education, domain]):
        flash('Please fill all fields!', 'warning')
        return redirect(url_for('index'))
    
    # Get top 3 careers
    top_careers = get_top_careers(skills, interests, education, domain)
    
    # Primary career analysis
    primary_career = top_careers[0][0]
    match_pct, missing_skills, roadmap = skill_gap_analysis(skills, primary_career)
    
    return render_template('result.html',
                         top_careers=top_careers,
                         primary_career=primary_career,
                         match_pct=match_pct,
                         missing_skills=missing_skills,
                         roadmap=roadmap,
                         inputs={'skills': skills, 'interests': interests, 'education': education, 'domain': domain})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    response = get_chat_response(data.get('message', ''))
    return jsonify({'response': response})

@app.route('/personality', methods=['POST'])
def personality():
    data = request.get_json()
    score = calculate_personality_score(data.get('answers', []))
    career = get_personality_career(score)
    return jsonify({'score': score, 'career': career})

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file'})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        text = extract_text_from_pdf(filepath)
        skills, gaps, recommendations = analyze_resume_skills(text)
        score = generate_resume_score(text)
        
        # Cleanup
        os.remove(filepath)
        
        return jsonify({
            'skills': skills,
            'gaps': gaps,
            'recommendations': recommendations,
            'score': score
        })
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/personality_test', methods=['GET'])
def personality_test():
    return render_template('personality_test.html')  # Create later

if __name__ == '__main__':
    print("🚀 Starting Professional AI Career Guidance System...")
    print("📱 Home: http://127.0.0.1:5000")
    print("💬 Chat API: /chat")
    print("📄 Resume: /upload")
    print("🧠 Personality: /personality")
    print("Press Ctrl+C to stop")
    app.run(debug=True, host='127.0.0.1', port=5000)

