"""
Views for Certificate Fraud Detection Application
"""
import os
import json
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.conf import settings
from django.utils import timezone
from PIL import Image

# Import models and forms
from .models import Certificate
from .forms import UserRegistrationForm, CertificateUploadForm

# Import AI models
from .ai_models.bert_model import BERTFraudDetector
from .ai_models.signature_model import SignatureDetector
from .ai_models.logo_model import LogoDetector
from .ai_models.stamp_verifier import StampVerifier

# Import utilities
from .utils.ocr import extract_text_from_file
from .utils.fraud_score import (
    calculate_final_fraud_score,
    get_risk_level,
    generate_recommendation
)

# PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

# Configure logging
logger = logging.getLogger(__name__)

# Initialize AI models (lazy loading)
_bert_detector = None
_signature_detector = None
_logo_detector = None
_stamp_verifier = None


def get_ai_models():
    """Initialize and return AI models (lazy loading)."""
    global _bert_detector, _signature_detector, _logo_detector, _stamp_verifier
    
    if _bert_detector is None:
        try:
            _bert_detector = BERTFraudDetector()
            logger.info("BERT fraud detector loaded")
        except Exception as e:
            logger.error(f"Error loading BERT model: {e}")
    
    if _signature_detector is None:
        try:
            _signature_detector = SignatureDetector()
            logger.info("Signature detector loaded")
        except Exception as e:
            logger.error(f"Error loading signature detector: {e}")
    
    if _logo_detector is None:
        try:
            _logo_detector = LogoDetector()
            logger.info("Logo detector loaded")
        except Exception as e:
            logger.error(f"Error loading logo detector: {e}")
    
    if _stamp_verifier is None:
        try:
            _stamp_verifier = StampVerifier()
            logger.info("Stamp verifier loaded")
        except Exception as e:
            logger.error(f"Error loading stamp verifier: {e}")
    
    return _bert_detector, _signature_detector, _logo_detector, _stamp_verifier


# ==================== Authentication Views ====================

def index(request):
    """Landing page - redirects to login or dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Certificate Fraud Detection System.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'register.html', {'form': form})


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page if specified
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ==================== Main Application Views ====================

@login_required
def dashboard(request):
    """Main dashboard showing recent certificates and stats."""
    user = request.user
    
    # Get user's certificates
    certificates = Certificate.objects.filter(user=user)[:10]
    
    # Calculate statistics
    total_certificates = Certificate.objects.filter(user=user).count()
    genuine_count = Certificate.objects.filter(user=user, result='genuine').count()
    suspicious_count = Certificate.objects.filter(user=user, result='suspicious').count()
    fraudulent_count = Certificate.objects.filter(user=user, result='fraudulent').count()
    
    # Recent activity
    recent_uploads = Certificate.objects.filter(user=user).order_by('-uploaded_at')[:5]
    
    context = {
        'certificates': certificates,
        'total_certificates': total_certificates,
        'genuine_count': genuine_count,
        'suspicious_count': suspicious_count,
        'fraudulent_count': fraudulent_count,
        'recent_uploads': recent_uploads,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def upload_certificate(request):
    """View for uploading and analyzing certificates."""
    if request.method == 'POST':
        form = CertificateUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save certificate record
            certificate = form.save(commit=False)
            certificate.user = request.user
            certificate.original_filename = request.FILES['certificate_file'].name
            certificate.file_extension = os.path.splitext(certificate.original_filename)[1].lower()
            certificate.file_size = request.FILES['certificate_file'].size
            certificate.status = 'processing'
            certificate.save()
            
            try:
                # Get file path
                file_path = certificate.certificate_file.path
                
                # Convert PDF to image if needed (for image processing)
                image_path = file_path
                temp_image = None
                
                if certificate.file_extension == '.pdf':
                    # For PDF, convert first page to image for analysis
                    try:
                        images = convert_pdf_to_images(file_path)
                        if images:
                            temp_image = os.path.join(settings.MEDIA_ROOT, 'temp', f'temp_{certificate.id}.png')
                            os.makedirs(os.path.dirname(temp_image), exist_ok=True)
                            images[0].save(temp_image)
                            image_path = temp_image
                    except Exception as e:
                        logger.error(f"Error converting PDF: {e}")
                
                # Run AI Analysis
                logger.info(f"Starting AI analysis for certificate {certificate.id}")
                
                # 1. Extract text using OCR
                extracted_text = extract_text_from_file(file_path)
                certificate.extracted_text = extracted_text
                
                # 2. Initialize AI models
                bert_detector, signature_detector, logo_detector, stamp_verifier = get_ai_models()
                
                # 3. Run text fraud detection
                text_result = {}
                if bert_detector and extracted_text:
                    text_result = bert_detector.predict(extracted_text)
                    certificate.text_fraud_score = text_result.get('fraud_probability', 0.0)
                
                # 4. Run signature detection (only for images)
                signature_result = {}
                if signature_detector and os.path.exists(image_path):
                    signature_result = signature_detector.detect(image_path)
                    certificate.signature_score = signature_result.get('similarity_score', 0.0)
                
                # 5. Run logo detection
                logo_result = {}
                if logo_detector and os.path.exists(image_path):
                    logo_result = logo_detector.verify_logo(image_path)
                    certificate.logo_score = logo_result.get('similarity_score', 0.0)
                
                # 6. Run stamp verification
                stamp_result = {}
                if stamp_verifier and os.path.exists(image_path):
                    stamp_result = stamp_verifier.detect_stamps(image_path)
                    certificate.stamp_score = stamp_result.get('stamp_score', 0.0)
                
                # 7. Calculate final fraud score
                final_result = calculate_final_fraud_score(
                    text_result,
                    signature_result,
                    logo_result,
                    stamp_result
                )
                
                certificate.final_fraud_score = final_result['final_fraud_score']
                certificate.result = final_result['classification']
                certificate.analysis_details = json.dumps(final_result['analysis_details'])
                certificate.processed_at = timezone.now()
                certificate.status = 'completed'
                
                # Clean up temp file
                if temp_image and os.path.exists(temp_image):
                    try:
                        os.remove(temp_image)
                    except:
                        pass
                
                certificate.save()
                
                messages.success(request, f'Certificate analysis completed! Result: {certificate.get_result_display()}')
                return redirect('result_detail', certificate_id=certificate.id)
                
            except Exception as e:
                logger.error(f"Error processing certificate: {e}")
                certificate.status = 'failed'
                certificate.save()
                messages.error(request, f'Error processing certificate: {str(e)}')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid form submission. Please check the file.')
    else:
        form = CertificateUploadForm()
    
    return render(request, 'upload.html', {'form': form})


@login_required
def result_detail(request, certificate_id):
    """View detailed results of a certificate analysis."""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    # Parse analysis details
    try:
        analysis_details = json.loads(certificate.analysis_details) if certificate.analysis_details else {}
    except:
        analysis_details = {}
    
    # Generate recommendation
    recommendation = generate_recommendation(
        certificate.result,
        certificate.final_fraud_score,
        analysis_details
    )
    
    # Get risk level
    risk_level = get_risk_level(certificate.final_fraud_score)
    
    context = {
        'certificate': certificate,
        'analysis_details': analysis_details,
        'recommendation': recommendation,
        'risk_level': risk_level,
    }
    
    return render(request, 'result.html', context)


@login_required
def certificate_history(request):
    """View history of all uploaded certificates."""
    certificates = Certificate.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Filter options
    filter_result = request.GET.get('result')
    if filter_result:
        certificates = certificates.filter(result=filter_result)
    
    context = {
        'certificates': certificates,
        'filter_result': filter_result,
    }
    
    return render(request, 'history.html', context)


@login_required
def delete_certificate(request, certificate_id):
    """Delete a certificate record."""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    if request.method == 'POST':
        # Delete the file
        if certificate.certificate_file:
            try:
                certificate.certificate_file.delete()
            except:
                pass
        
        certificate.delete()
        messages.success(request, 'Certificate deleted successfully.')
    else:
        messages.error(request, 'Invalid request method.')
    
    return redirect('history')


# ==================== Report Download Views ====================

@login_required
def download_pdf_report(request, certificate_id):
    """Generate and download PDF fraud report."""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    # Parse analysis details
    try:
        analysis_details = json.loads(certificate.analysis_details) if certificate.analysis_details else {}
    except:
        analysis_details = {}
    
    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fraud_report_{certificate.id}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
    )
    story.append(Paragraph("Certificate Fraud Detection Report", title_style))
    story.append(Spacer(1, 20))
    
    # Certificate Info
    story.append(Paragraph("Certificate Information", styles['Heading2']))
    info_data = [
        ['Filename:', certificate.original_filename],
        ['Upload Date:', certificate.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')],
        ['File Type:', certificate.file_extension.upper()],
        ['File Size:', f"{certificate.file_size / 1024:.2f} KB"],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Analysis Results
    story.append(Paragraph("Analysis Results", styles['Heading2']))
    result_color = colors.green if certificate.result == 'genuine' else (colors.orange if certificate.result == 'suspicious' else colors.red)
    
    result_data = [
        ['Final Fraud Score:', f"{certificate.final_fraud_score}%"],
        ['Result:', certificate.result.upper()],
        ['Risk Level:', get_risk_level(certificate.final_fraud_score)],
    ]
    result_table = Table(result_data, colWidths=[2*inch, 4*inch])
    result_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (1, 1), (1, 1), result_color),
    ]))
    story.append(result_table)
    story.append(Spacer(1, 20))
    
    # Individual Scores
    story.append(Paragraph("Component Analysis", styles['Heading2']))
    scores_data = [
        ['Component', 'Score', 'Assessment'],
        ['Text Analysis', f"{certificate.text_fraud_score}%", 'Fraud Probability'],
        ['Signature', f"{certificate.signature_score}%", 'Similarity Match'],
        ['Logo', f"{certificate.logo_score}%", 'Similarity Match'],
        ['Stamp', f"{certificate.stamp_score}%", 'Presence Score'],
    ]
    scores_table = Table(scores_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    scores_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
    ]))
    story.append(scores_table)
    story.append(Spacer(1, 20))
    
    # Recommendation
    story.append(Paragraph("Recommendation", styles['Heading2']))
    story.append(Paragraph(generate_recommendation(certificate.result, certificate.final_fraud_score, analysis_details), styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
    )
    story.append(Paragraph(f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
    story.append(Paragraph("Certificate Fraud Detection System - AI-Powered Analysis", footer_style))
    
    doc.build(story)
    return response


@login_required
def download_json_report(request, certificate_id):
    """Generate and download JSON fraud report."""
    certificate = get_object_or_404(Certificate, id=certificate_id, user=request.user)
    
    # Parse analysis details
    try:
        analysis_details = json.loads(certificate.analysis_details) if certificate.analysis_details else {}
    except:
        analysis_details = {}
    
    # Create JSON data
    report_data = {
        'report_id': f"FRAUD-{certificate.id:06d}",
        'generated_at': datetime.now().isoformat(),
        'certificate': {
            'id': certificate.id,
            'filename': certificate.original_filename,
            'upload_date': certificate.uploaded_at.isoformat(),
            'file_type': certificate.file_extension,
            'file_size_bytes': certificate.file_size,
        },
        'analysis_results': {
            'final_fraud_score': certificate.final_fraud_score,
            'result': certificate.result,
            'risk_level': get_risk_level(certificate.final_fraud_score),
            'status': certificate.status,
            'processed_at': certificate.processed_at.isoformat() if certificate.processed_at else None,
        },
        'component_scores': {
            'text_analysis': {
                'fraud_probability': certificate.text_fraud_score,
                'details': analysis_details.get('text_analysis', {}),
            },
            'signature_analysis': {
                'similarity_score': certificate.signature_score,
                'details': analysis_details.get('signature_analysis', {}),
            },
            'logo_analysis': {
                'similarity_score': certificate.logo_score,
                'details': analysis_details.get('logo_analysis', {}),
            },
            'stamp_analysis': {
                'presence_score': certificate.stamp_score,
                'details': analysis_details.get('stamp_analysis', {}),
            },
        },
        'extracted_text': certificate.extracted_text[:1000] + '...' if len(certificate.extracted_text) > 1000 else certificate.extracted_text,
        'recommendation': generate_recommendation(certificate.result, certificate.final_fraud_score, analysis_details),
    }
    
    # Return JSON response
    response = HttpResponse(
        json.dumps(report_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="fraud_report_{certificate.id}.json"'
    return response


# ==================== Helper Functions ====================

def convert_pdf_to_images(pdf_path):
    """Convert PDF to list of PIL Images."""
    try:
        from pdf2image import convert_from_path
        return convert_from_path(pdf_path)
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        return []
