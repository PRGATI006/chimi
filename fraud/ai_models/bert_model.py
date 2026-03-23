"""
BERT-based Text Fraud Detection Model
Uses pretrained BERT model for binary classification of certificate text as Fraud or Genuine.
"""
import os
import torch
from transformers import BertTokenizer, BertForSequenceClassification, BertModel
import numpy as np
from django.conf import settings


class BERTFraudDetector:
    """
    BERT-based fraud detection for certificate text.
    Uses bert-base-uncased with a classification head.
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the BERT fraud detector.
        
        Args:
            model_path: Path to fine-tuned model. If None, uses pretrained BERT.
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = getattr(settings, 'BERT_MODEL_NAME', 'bert-base-uncased')
        self.max_length = getattr(settings, 'BERT_MAX_LENGTH', 512)
        
        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
        
        # Load model - either fine-tuned or base for feature extraction
        if model_path and os.path.exists(model_path):
            self.model = BertForSequenceClassification.from_pretrained(
                model_path,
                num_labels=2
            )
        else:
            # Use base BERT for sentiment-like classification
            # In production, you would fine-tune this on certificate fraud data
            self.model = BertForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2
            )
        
        self.model.to(self.device)
        self.model.eval()
        
        # Keywords that may indicate fraud (fallback if model not fine-tuned)
        self.fraud_keywords = [
            'fake', 'forged', 'counterfeit', 'invalid', 'unauthorized',
            'duplicate', 'falsified', 'tampered', 'modified', 'altered',
            'expired', 'revoked', 'suspended', 'invalid', 'void'
        ]
        
        self.genuine_keywords = [
            'authentic', 'verified', 'valid', 'genuine', 'official',
            'authorized', 'legitimate', 'certified', 'original', 'true'
        ]
    
    def preprocess_text(self, text):
        """Clean and preprocess text for BERT."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Truncate to max length
        if len(text) > self.max_length * 4:  # Approximate char to token ratio
            text = text[:self.max_length * 4]
        
        return text
    
    def predict(self, text):
        """
        Predict fraud probability for certificate text.
        
        Args:
            text: Extracted text from certificate
            
        Returns:
            dict: Contains fraud_probability (0-100), confidence, and details
        """
        if not text or len(text.strip()) < 10:
            return {
                'fraud_probability': 0.0,
                'confidence': 0.0,
                'details': 'Text too short for analysis',
                'method': 'insufficient_data'
            }
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Tokenize
        inputs = self.tokenizer(
            processed_text,
            return_tensors='pt',
            max_length=self.max_length,
            truncation=True,
            padding=True
        )
        
        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)
        
        # Get fraud probability (class 1)
        fraud_prob = probabilities[0][1].item()
        
        # Calculate confidence
        confidence = max(probabilities[0]).item()
        
        # Additional keyword-based analysis for better results
        text_lower = text.lower()
        
        # Count fraud indicators
        fraud_count = sum(1 for keyword in self.fraud_keywords if keyword in text_lower)
        genuine_count = sum(1 for keyword in self.genuine_keywords if keyword in text_lower)
        
        # Combine model prediction with keyword analysis
        keyword_score = 0.0
        if fraud_count > 0 or genuine_count > 0:
            total = fraud_count + genuine_count
            keyword_score = (fraud_count / total) * 100
        
        # Weighted combination (model gets more weight)
        final_fraud_prob = (fraud_prob * 100 * 0.7) + (keyword_score * 0.3)
        
        return {
            'fraud_probability': round(final_fraud_prob, 2),
            'confidence': round(confidence * 100, 2),
            'model_probability': round(fraud_prob * 100, 2),
            'keyword_score': round(keyword_score, 2),
            'fraud_keywords_found': fraud_count,
            'genuine_keywords_found': genuine_count,
            'details': f"Found {fraud_count} fraud indicators and {genuine_count} genuine indicators",
            'method': 'bert_keyword_hybrid'
        }
    
    def analyze_text_features(self, text):
        """Analyze additional text features that may indicate fraud."""
        features = {}
        
        # Text length
        features['text_length'] = len(text)
        features['word_count'] = len(text.split())
        
        # Check for common patterns in forged certificates
        features['has_date'] = bool(DateValidator.has_valid_date(text))
        
        # Check for unusual characters
        unusual_chars = sum(1 for c in text if ord(c) > 127)
        features['unusual_char_ratio'] = unusual_chars / max(len(text), 1)
        
        return features


class DateValidator:
    """Helper class for date validation in certificates."""
    
    @staticmethod
    def has_valid_date(text):
        """Check if text contains a potentially valid date."""
        import re
        # Match common date formats
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',
            r'\d{1,2}-\d{1,2}-\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False


def load_model():
    """Helper function to load the model globally."""
    global _bert_model
    if '_bert_model' not in globals():
        _bert_model = BERTFraudDetector()
    return _bert_model
