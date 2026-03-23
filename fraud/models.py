"""
Models for Certificate Fraud Detection Application
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os


def certificate_upload_path(instance, filename):
    """Generate upload path for certificate files"""
    ext = filename.split('.')[-1].lower()
    filename = f"certificate_{instance.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
    return os.path.join('uploads/certificates/', filename)


class Certificate(models.Model):
    """
    Model to store uploaded certificates and their fraud analysis results.
    """
    # Status choices
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    RESULT_CHOICES = [
        ('genuine', 'Genuine'),
        ('suspicious', 'Suspicious'),
        ('fraudulent', 'Fraudulent'),
    ]
    
    # User relation
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    
    # Certificate file
    certificate_file = models.FileField(upload_to=certificate_upload_path)
    original_filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=10)
    file_size = models.IntegerField(default=0)
    
    # Upload timestamp
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # OCR extracted text
    extracted_text = models.TextField(blank=True, default='')
    
    # AI Analysis Results
    text_fraud_score = models.FloatField(default=0.0)  # 0-100
    signature_score = models.FloatField(default=0.0)  # 0-100
    logo_score = models.FloatField(default=0.0)  # 0-100
    stamp_score = models.FloatField(default=0.0)  # 0-100
    
    # Final fraud detection result
    final_fraud_score = models.FloatField(default=0.0)  # 0-100
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='genuine')
    
    # Analysis details (JSON stored as text)
    analysis_details = models.TextField(blank=True, default='{}')
    
    # Flag for suspicious items
    is_flagged = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, default='')
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Certificate'
        verbose_name_plural = 'Certificates'
    
    def __str__(self):
        return f"{self.original_filename} - {self.result} ({self.final_fraud_score}%)"
    
    @property
    def get_status_display_class(self):
        """Return CSS class for status badge"""
        status_classes = {
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
        }
        return status_classes.get(self.status, 'secondary')
    
    @property
    def get_result_display_class(self):
        """Return CSS class for result badge"""
        result_classes = {
            'genuine': 'success',
            'suspicious': 'warning',
            'fraudulent': 'danger',
        }
        return result_classes.get(self.result, 'secondary')
