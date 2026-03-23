"""
Configuration settings for the Certificate Fraud Detection application.
Optimized for 8GB RAM laptop (CPU only).
"""
import os

class Config:
    """Base configuration."""
    # Secret key for sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File uploads
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    
    # Create upload directories
    LOGOS_FOLDER = os.path.join('static', 'logos')
    SIGNATURES_FOLDER = os.path.join('static', 'signatures')
    
    # BERT model settings (lightweight for CPU)
    BERT_MODEL_NAME = 'distilbert-base-uncased'
    BERT_MAX_LENGTH = 256
    
    # Page settings
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
