"""
Certificate Fraud Detection Web Application
Main Flask Application

AI-Based Certificate Fraud Detection System using:
- DistilBERT for text analysis
- SSIM for signature verification
- OpenCV for logo detection
- Hough Circle Transform for stamp verification
"""
import os
import json
import uuid
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import config
from models import db, User, Certificate
from forms import RegistrationForm, LoginForm, UploadForm
from utils import extract_text, calculate_overall_fraud_score, generate_json_report, generate_pdf_report
from ai_models import get_nlp_detector, get_signature_checker, get_logo_checker, get_stamp_checker


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['LOGOS_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SIGNATURES_FOLDER'], exist_ok=True)
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app):
    """Register all application routes."""
    
    @app.route('/')
    def index():
        """Home page."""
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            # Check if user exists
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already taken', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_admin=False
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login."""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                
                # Redirect to admin if admin user
                if user.is_admin:
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout."""
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard."""
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        
        certificates = Certificate.query.filter_by(
            user_id=current_user.id
        ).order_by(Certificate.created_at.desc()).all()
        
        return render_template('dashboard.html', certificates=certificates)
    
    @app.route('/upload', methods=['GET', 'POST'])
    @login_required
    def upload():
        """Upload and analyze certificate."""
        form = UploadForm()
        
        if form.validate_on_submit():
            file = form.certificate.data
            
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(request.url)
            
            # Check file extension
            allowed = app.config['ALLOWED_EXTENSIONS']
            ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if ext not in allowed:
                flash(f'Invalid file type. Allowed: {", ".join(allowed)}', 'danger')
                return redirect(request.url)
            
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(filepath)
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'danger')
                return redirect(request.url)
            
            # Analyze certificate
            try:
                result = analyze_certificate(filepath, current_user.id, filename, unique_filename)
                
                if result:
                    flash('Certificate analyzed successfully!', 'success')
                    return redirect(url_for('result', certificate_id=result.id))
                else:
                    flash('Error analyzing certificate', 'danger')
            except Exception as e:
                flash(f'Error during analysis: {str(e)}', 'danger')
            
            return redirect(url_for('dashboard'))
        
        return render_template('upload.html', form=form)
    
    @app.route('/result/<int:certificate_id>')
    @login_required
    def result(certificate_id):
        """View fraud detection result."""
        certificate = Certificate.query.get_or_404(certificate_id)
        
        # Check ownership or admin
        if certificate.user_id != current_user.id and not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        # Parse detection details
        detection_details = {}
        if certificate.detection_details:
            try:
                detection_details = json.loads(certificate.detection_details)
            except:
                pass
        
        return render_template('result.html', certificate=certificate, detection_details=detection_details)
    
    @app.route('/download/json/<int:certificate_id>')
    @login_required
    def download_json(certificate_id):
        """Download JSON report."""
        certificate = Certificate.query.get_or_404(certificate_id)
        
        if certificate.user_id != current_user.id and not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        report = generate_json_report(certificate)
        return jsonify(report)
    
    @app.route('/download/pdf/<int:certificate_id>')
    @login_required
    def download_pdf(certificate_id):
        """Download PDF report."""
        certificate = Certificate.query.get_or_404(certificate_id)
        
        if certificate.user_id != current_user.id and not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        pdf_path = generate_pdf_report(certificate)
        
        if pdf_path and os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=True, download_name=f'fraud_report_{certificate.id}.pdf')
        else:
            flash('Error generating PDF', 'danger')
            return redirect(url_for('result', certificate_id=certificate_id))
    
    @app.route('/delete/<int:certificate_id>')
    @login_required
    def delete_certificate(certificate_id):
        """Delete a certificate."""
        certificate = Certificate.query.get_or_404(certificate_id)
        
        if certificate.user_id != current_user.id and not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        # Delete file
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], certificate.filepath)
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
        
        # Delete from database
        db.session.delete(certificate)
        db.session.commit()
        
        flash('Certificate deleted', 'success')
        
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    # Admin routes
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        """Admin dashboard."""
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('dashboard'))
        
        filter_type = request.args.get('filter', 'all')
        
        if filter_type == 'suspicious':
            certificates = Certificate.query.filter_by(is_suspicious=True).order_by(Certificate.created_at.desc()).all()
        else:
            certificates = Certificate.query.order_by(Certificate.created_at.desc()).all()
        
        # Statistics
        total = Certificate.query.count()
        suspicious = Certificate.query.filter_by(is_suspicious=True).count()
        avg_score = db.session.query(db.func.avg(Certificate.overall_fraud_score)).scalar() or 0
        
        stats = {
            'total': total,
            'suspicious': suspicious,
            'avg_score': round(avg_score, 2)
        }
        
        return render_template('admin.html', certificates=certificates, stats=stats, filter_type=filter_type)
    
    @app.route('/admin/toggle/<int:certificate_id>')
    @login_required
    def toggle_suspicious(certificate_id):
        """Toggle suspicious flag."""
        if not current_user.is_admin:
            flash('Access denied', 'danger')
            return redirect(url_for('dashboard'))
        
        certificate = Certificate.query.get_or_404(certificate_id)
        certificate.is_suspicious = not certificate.is_suspicious
        db.session.commit()
        
        flash(f'Suspicious status updated', 'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('error.html', error='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error.html', error='Internal server error'), 500


def analyze_certificate(filepath, user_id, filename, unique_filename):
    """
    Analyze a certificate for fraud.
    
    Args:
        filepath: Path to the certificate file
        user_id: ID of the user uploading the certificate
        filename: Original filename
        unique_filename: Unique filename for storage
        
    Returns:
        Certificate object or None
    """
    # Initialize AI models
    nlp_detector = get_nlp_detector()
    signature_checker = get_signature_checker()
    logo_checker = get_logo_checker()
    stamp_checker = get_stamp_checker()
    
    # Extract text using OCR
    extracted_text = ""
    try:
        extracted_text = extract_text(filepath)
    except Exception as e:
        print(f"OCR Error: {e}")
        extracted_text = ""
    
    # Initialize detection results
    detection_results = {
        'text_analysis': {},
        'signature_analysis': {},
        'logo_analysis': {},
        'stamp_analysis': {}
    }
    
    # 1. Text Fraud Analysis (NLP)
    text_fraud_score = 0.0
    try:
        if extracted_text:
            text_fraud_score = nlp_detector.analyze_text(extracted_text) * 100
        detection_results['text_analysis'] = {
            'fraud_score': text_fraud_score,
            'text_length': len(extracted_text)
        }
    except Exception as e:
        print(f"Text analysis error: {e}")
    
    # 2. Signature Detection (SSIM)
    signature_detected = False
    signature_fraud_score = 0.0
    try:
        sig_result = signature_checker.analyze_signature(filepath)
        signature_detected = sig_result['detected']
        signature_fraud_score = sig_result['fraud_score'] * 100
        detection_results['signature_analysis'] = sig_result
    except Exception as e:
        print(f"Signature check error: {e}")
    
    # 3. Logo Detection (OpenCV)
    logo_detected = False
    logo_fraud_score = 0.0
    try:
        logo_result = logo_checker.analyze_logo(filepath)
        logo_detected = logo_result['detected']
        logo_fraud_score = logo_result['fraud_score'] * 100
        detection_results['logo_analysis'] = logo_result
    except Exception as e:
        print(f"Logo check error: {e}")
    
    # 4. Stamp Verification (Hough Circle)
    stamp_detected = False
    stamp_fraud_score = 0.0
    try:
        stamp_result = stamp_checker.analyze_stamp(filepath)
        stamp_detected = stamp_result['detected']
        stamp_fraud_score = stamp_result['fraud_score'] * 100
        detection_results['stamp_analysis'] = stamp_result
    except Exception as e:
        print(f"Stamp check error: {e}")
    
    # Calculate overall fraud score
    overall_fraud_score = calculate_overall_fraud_score(
        text_fraud_score,
        signature_fraud_score,
        logo_fraud_score,
        stamp_fraud_score
    )
    
    # Determine if suspicious (score > 50)
    is_suspicious = overall_fraud_score > 50
    
    # Create certificate record
    certificate = Certificate(
        user_id=user_id,
        filename=filename,
        filepath=unique_filename,
        extracted_text=extracted_text[:1000],  # Limit text storage
        text_fraud_score=text_fraud_score,
        signature_fraud_score=signature_fraud_score,
        logo_fraud_score=logo_fraud_score,
        stamp_fraud_score=stamp_fraud_score,
        overall_fraud_score=overall_fraud_score,
        signature_detected=signature_detected,
        logo_detected=logo_detected,
        stamp_detected=stamp_detected,
        detection_details=json.dumps(detection_results),
        is_suspicious=is_suspicious
    )
    
    db.session.add(certificate)
    db.session.commit()
    
    return certificate


def init_database(app):
    """Initialize database with tables and default admin user."""
    with app.app_context():
        db.create_all()
        
        # Create admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create test user
            test_user = User(
                username='user',
                email='user@example.com',
                is_admin=False
            )
            test_user.set_password('user123')
            db.session.add(test_user)
            
            db.session.commit()
            print("Database initialized with default users!")
        else:
            print("Database already initialized.")


# Main application
if __name__ == '__main__':
    app = create_app('development')
    init_database(app)
    app.run(debug=True, host='127.0.0.1', port=5000)
