"""
Database models for the Certificate Fraud Detection application.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    certificates = db.relationship('Certificate', backref='user', lazy=True)

    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Certificate(db.Model):
    """Certificate model to store uploaded certificates and fraud analysis."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    
    # Fraud scores from each model (0-100)
    text_fraud_score = db.Column(db.Float, default=0.0)
    signature_fraud_score = db.Column(db.Float, default=0.0)
    logo_fraud_score = db.Column(db.Float, default=0.0)
    stamp_fraud_score = db.Column(db.Float, default=0.0)
    overall_fraud_score = db.Column(db.Float, default=0.0)
    
    # Detection details (JSON string)
    signature_detected = db.Column(db.Boolean, default=False)
    logo_detected = db.Column(db.Boolean, default=False)
    stamp_detected = db.Column(db.Boolean, default=False)
    
    detection_details = db.Column(db.Text, nullable=True)
    
    is_suspicious = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Certificate {self.id}: {self.filename}>'
