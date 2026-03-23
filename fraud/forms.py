"""
Forms for Certificate Fraud Detection Application
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Certificate
from django.core.validators import FileExtensionValidator


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with validation.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['email', 'first_name', 'last_name']:
                field.widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class CertificateUploadForm(forms.ModelForm):
    """
    Form for uploading certificate files with validation.
    """
    
    class Meta:
        model = Certificate
        fields = ['certificate_file']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['certificate_file'].widget.attrs.update({
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    
    def clean_certificate_file(self):
        """Validate the uploaded certificate file."""
        file = self.cleaned_data.get('certificate_file')
        
        if not file:
            raise forms.ValidationError("Please upload a certificate file.")
        
        # Get file extension
        ext = file.name.split('.')[-1].lower()
        
        # Validate extension
        allowed_extensions = ['pdf', 'jpg', 'jpeg', 'png']
        if ext not in allowed_extensions:
            raise forms.ValidationError(
                f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file.size > max_size:
            raise forms.ValidationError(
                f"File size too large. Maximum allowed size is 5MB."
            )
        
        # Validate MIME type
        allowed_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
        if hasattr(file, 'content_type') and file.content_type not in allowed_mime_types:
            raise forms.ValidationError(
                f"Invalid file type. Please upload PDF, JPG, or PNG files."
            )
        
        return file


class CertificateAdminForm(forms.ModelForm):
    """
    Form for admin to add notes to certificates.
    """
    
    class Meta:
        model = Certificate
        fields = ['admin_notes', 'is_flagged']
    
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    is_flagged = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=False
    )
