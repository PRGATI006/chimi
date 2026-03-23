"""
NLP Model for text-based fraud detection using DistilBERT.
Optimized for CPU and 8GB RAM.
"""
import os
import warnings
warnings.filterwarnings('ignore')

# Configure environment for CPU
os.environ['CUDA_VISIBLE_DEVICES'] = ''

class NLPFraudDetector:
    """
    DistilBERT-based fraud detector for certificate text analysis.
    Uses a rule-based approach combined with sentiment analysis.
    Lightweight and CPU-friendly.
    """
    
    # Common fraud keywords in certificates
    FRAUD_KEYWORDS = [
        'urgent', 'immediate action', 'click here', 'verify now',
        'expire', 'suspended', 'claim now', 'free certificate',
        'limited time', 'act now', 'winner', 'prize', 'congratulations',
        'payment required', 'bank details', 'credit card', 'update now',
        'suspicious', 'unauthorized', 'fake', 'forged'
    ]
    
    # Genuine certificate keywords
    GENUINE_KEYWORDS = [
        'certified', 'certificate of', 'completion', 'achievement',
        'awarded to', 'successfully completed', 'verified',
        'authentic', 'official', 'issued by', 'authorised'
    ]
    
    def __init__(self):
        """Initialize the NLP detector."""
        self.model_name = 'distilbert-base-uncased'
        self.tokenizer = None
        self.model = None
        self.is_loaded = False
        
    def load_model(self):
        """
        Load the DistilBERT model.
        Note: For CPU efficiency, we use rule-based detection instead of full model.
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            
            print("Loading DistilBERT model...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2
            )
            self.model.eval()  # Set to evaluation mode
            self.is_loaded = True
            print("DistilBERT model loaded successfully!")
            return True
        except Exception as e:
            print(f"Warning: Could not load DistilBERT model: {e}")
            print("Using rule-based fraud detection instead.")
            self.is_loaded = False
            return False
    
    def analyze_text(self, text):
        """
        Analyze text for fraud indicators.
        Returns a fraud score between 0.0 (genuine) and 1.0 (fraudulent).
        """
        if not text or len(text.strip()) == 0:
            return 0.0
        
        text_lower = text.lower()
        
        # Count fraud and genuine keywords
        fraud_count = sum(1 for keyword in self.FRAUD_KEYWORDS if keyword in text_lower)
        genuine_count = sum(1 for keyword in self.GENUINE_KEYWORDS if keyword in text_lower)
        
        # Calculate base score using keyword matching
        if fraud_count + genuine_count == 0:
            base_score = 0.3  # Neutral
        else:
            # More fraud keywords = higher score
            base_score = fraud_count / (fraud_count + genuine_count + 1)
        
        # Check for suspicious patterns
        suspicious_patterns = [
            len(text) > 5000,  # Very long text
            text.count('!') > 3,  # Multiple exclamation marks
            text.isupper(),  # All caps
            'http://' in text_lower or 'https://' in text_lower,  # Contains URLs
            '$' in text or '₹' in text or 'USD' in text_upper,  # Money mentions
        ]
        
        # Add penalty for suspicious patterns
        pattern_penalty = sum(suspicious_patterns) * 0.1
        
        # Try ML model if available
        if self.is_loaded and self.model and self.tokenizer:
            try:
                import torch
                inputs = self.tokenizer(
                    text[:512],  # Limit to first 512 tokens
                    return_tensors="pt",
                    truncation=True,
                    max_length=256
                )
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probabilities = torch.softmax(outputs.logits, dim=1)
                    # Get probability of fraud (class 1)
                    ml_score = probabilities[0][1].item()
                
                # Combine keyword and ML scores
                final_score = (base_score * 0.4 + ml_score * 0.6 + pattern_penalty)
            except Exception as e:
                print(f"ML inference error: {e}")
                final_score = base_score + pattern_penalty
        else:
            final_score = base_score + pattern_penalty
        
        # Clamp score between 0 and 1
        return min(max(final_score, 0.0), 1.0)


# Global instance (lazy loading)
_nlp_detector = None

def get_nlp_detector():
    """Get or create the NLP detector instance."""
    global _nlp_detector
    if _nlp_detector is None:
        _nlp_detector = NLPFraudDetector()
        _nlp_detector.load_model()
    return _nlp_detector
