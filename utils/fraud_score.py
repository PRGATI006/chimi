"""
Fraud score calculation utility.
Calculates overall fraud score from individual model scores.
"""
import json
from datetime import datetime


def calculate_overall_fraud_score(text_score, signature_score, logo_score, stamp_score):
    """
    Calculate overall fraud score from individual component scores.
    
    Args:
        text_score: Score from text analysis (0-100)
        signature_score: Score from signature check (0-100)
        logo_score: Score from logo check (0-100)
        stamp_score: Score from stamp check (0-100)
    
    Returns:
        Overall fraud score (0-100)
    """
    # Weights for each component
    # Text analysis is most important for fraud detection
    weights = {
        'text': 0.35,
        'signature': 0.20,
        'logo': 0.25,
        'stamp': 0.20
    }
    
    # Calculate weighted average
    overall = (
        text_score * weights['text'] +
        signature_score * weights['signature'] +
        logo_score * weights['logo'] +
        stamp_score * weights['stamp']
    )
    
    return round(overall, 2)


def generate_json_report(certificate):
    """
    Generate JSON report for a certificate.
    
    Args:
        certificate: Certificate model instance
        
    Returns:
        Dictionary with report data
    """
    # Parse detection details if available
    detection_details = {}
    if certificate.detection_details:
        try:
            detection_details = json.loads(certificate.detection_details)
        except:
            pass
    
    report = {
        'certificate_id': certificate.id,
        'filename': certificate.filename,
        'upload_date': certificate.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'extracted_text': certificate.extracted_text[:500] if certificate.extracted_text else "No text extracted",
        'fraud_scores': {
            'text_analysis': round(certificate.text_fraud_score, 2),
            'signature_check': round(certificate.signature_fraud_score, 2),
            'logo_check': round(certificate.logo_fraud_score, 2),
            'stamp_check': round(certificate.stamp_fraud_score, 2)
        },
        'overall_fraud_score': round(certificate.overall_fraud_score, 2),
        'is_suspicious': certificate.is_suspicious,
        'detection_details': detection_details
    }
    
    return report


def generate_pdf_report(certificate, output_path=None):
    """
    Generate PDF report for a certificate.
    
    Args:
        certificate: Certificate model instance
        output_path: Path to save PDF (optional)
        
    Returns:
        Path to generated PDF
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import inch
        
        # Parse detection details if available
        detection_details = {}
        if certificate.detection_details:
            try:
                detection_details = json.loads(certificate.detection_details)
            except:
                pass
        
        # Create PDF
        if output_path is None:
            output_path = f'fraud_report_{certificate.id}.pdf'
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph('Certificate Fraud Detection Report', title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Certificate Info
        story.append(Paragraph('Certificate Information', styles['Heading2']))
        info_data = [
            ['Certificate ID:', str(certificate.id)],
            ['Filename:', certificate.filename],
            ['Upload Date:', certificate.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Status:', 'SUSPICIOUS' if certificate.is_suspicious else 'Normal']
        ]
        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Fraud Scores
        story.append(Paragraph('Fraud Analysis Scores', styles['Heading2']))
        scores_data = [
            ['Analysis Type', 'Score (%)'],
            ['Text Analysis (NLP)', f"{certificate.text_fraud_score:.2f}"],
            ['Signature Check (SSIM)', f"{certificate.signature_fraud_score:.2f}"],
            ['Logo Detection', f"{certificate.logo_fraud_score:.2f}"],
            ['Stamp Verification', f"{certificate.stamp_fraud_score:.2f}"],
            ['OVERALL FRAUD SCORE', f"{certificate.overall_fraud_score:.2f}"]
        ]
        scores_table = Table(scores_data, colWidths=[3 * inch, 2 * inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Detection Details
        if detection_details:
            story.append(Paragraph('Detection Details', styles['Heading2']))
            
            for key, value in detection_details.items():
                if isinstance(value, dict):
                    story.append(Paragraph(f"<b>{key}:</b>", styles['Heading3']))
                    for k, v in value.items():
                        story.append(Paragraph(f"  {k}: {v}", styles['Normal']))
                else:
                    story.append(Paragraph(f"<b>{key}:</b> {value}", styles['Normal']))
                story.append(Spacer(1, 0.1 * inch))
        
        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        
        return output_path
        
    except Exception as e:
        print(f"Error generating PDF report: {e}")
        return None
