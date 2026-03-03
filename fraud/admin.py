"""
Django Admin Configuration for Fraud Detection Application
"""
from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """
    Admin configuration for Certificate model.
    """
    list_display = [
        'id',
        'original_filename',
        'user',
        'uploaded_at',
        'status',
        'final_fraud_score',
        'result',
        'is_flagged',
    ]
    
    list_filter = [
        'status',
        'result',
        'is_flagged',
        'uploaded_at',
    ]
    
    search_fields = [
        'original_filename',
        'user__username',
        'user__email',
        'extracted_text',
    ]
    
    readonly_fields = [
        'user',
        'original_filename',
        'file_extension',
        'file_size',
        'uploaded_at',
        'processed_at',
        'extracted_text',
        'text_fraud_score',
        'signature_score',
        'logo_score',
        'stamp_score',
        'final_fraud_score',
        'result',
        'analysis_details',
    ]
    
    fieldsets = (
        ('File Information', {
            'fields': (
                'user',
                'certificate_file',
                'original_filename',
                'file_extension',
                'file_size',
                'uploaded_at',
                'processed_at',
                'status',
            )
        }),
        ('OCR & Text Analysis', {
            'fields': (
                'extracted_text',
                'text_fraud_score',
            )
        }),
        ('AI Detection Results', {
            'fields': (
                'signature_score',
                'logo_score',
                'stamp_score',
                'final_fraud_score',
                'result',
            )
        }),
        ('Analysis Details', {
            'fields': (
                'analysis_details',
            )
        }),
        ('Admin Actions', {
            'fields': (
                'is_flagged',
                'admin_notes',
            )
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'uploaded_at'
    
    def has_add_permission(self, request):
        """Prevent adding certificates directly from admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but limit changes."""
        if obj is None:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting certificates."""
        return True
