"""
Fraud Score Calculation Utility
Combines all AI detection results to calculate final fraud score.
"""
import json
import logging

logger = logging.getLogger(__name__)


def calculate_final_fraud_score(text_result, signature_result, logo_result, stamp_result):
    """
    Calculate the final fraud score by combining all detection results.
    
    Args:
        text_result: dict - Result from BERT text fraud detection
        signature_result: dict - Result from signature detection
        logo_result: dict - Result from logo detection
        stamp_result: dict - Result from stamp verification
        
    Returns:
        dict: Final fraud score and classification
    """
    # Default weights for each detection component
    weights = {
        'text': 0.35,        # Text analysis is most important
        'signature': 0.25,   # Signature verification
        'logo': 0.25,       # Logo verification
        'stamp': 0.15,      # Stamp verification
    }
    
    # Get individual scores (convert to 0-100 scale where higher = more suspicious)
    text_score = text_result.get('fraud_probability', 0.0) if text_result else 0.0
    
    # Signature: similarity score - higher similarity = lower fraud
    # So we invert: higher similarity = more genuine
    signature_sim = signature_result.get('similarity_score', 0.0) if signature_result else 0.0
    signature_score = max(0, 100 - signature_sim)  # Invert: high similarity = low fraud
    
    # Logo: similar logic - high similarity = genuine
    logo_sim = logo_result.get('similarity_score', 0.0) if logo_result else 0.0
    logo_score = max(0, 100 - logo_sim)
    
    # Stamp: presence of stamp indicates authenticity
    stamp_score = stamp_result.get('stamp_score', 0.0) if stamp_result else 0.0
    # Invert: high stamp score = genuine, low stamp score = suspicious
    stamp_score_inverted = max(0, 100 - stamp_score)
    
    # Calculate weighted final score
    final_score = (
        text_score * weights['text'] +
        signature_score * weights['signature'] +
        logo_score * weights['logo'] +
        stamp_score_inverted * weights['stamp']
    )
    
    # Determine classification based on final score
    if final_score < 30:
        classification = 'genuine'
    elif final_score < 60:
        classification = 'suspicious'
    else:
        classification = 'fraudulent'
    
    # Prepare detailed analysis
    analysis_details = {
        'text_analysis': {
            'fraud_probability': text_score,
            'method': text_result.get('method', 'unknown') if text_result else 'N/A',
            'details': text_result.get('details', '') if text_result else '',
        },
        'signature_analysis': {
            'similarity_score': signature_sim,
            'fraud_indicator': signature_score,
            'has_signature': signature_result.get('has_signature', False) if signature_result else False,
            'method': signature_result.get('method', 'unknown') if signature_result else 'N/A',
        },
        'logo_analysis': {
            'similarity_score': logo_sim,
            'fraud_indicator': logo_score,
            'has_logo': logo_result.get('has_logo', False) if logo_result else False,
            'method': logo_result.get('method', 'unknown') if logo_result else 'N/A',
        },
        'stamp_analysis': {
            'presence_score': stamp_score,
            'fraud_indicator': stamp_score_inverted,
            'has_stamp': stamp_result.get('has_stamp', False) if stamp_result else False,
            'method': stamp_result.get('method', 'unknown') if stamp_result else 'N/A',
        },
        'weights_used': weights,
        'score_breakdown': {
            'text_contribution': round(text_score * weights['text'], 2),
            'signature_contribution': round(signature_score * weights['signature'], 2),
            'logo_contribution': round(logo_score * weights['logo'], 2),
            'stamp_contribution': round(stamp_score_inverted * weights['stamp'], 2),
        }
    }
    
    return {
        'final_fraud_score': round(final_score, 2),
        'classification': classification,
        'text_score': round(text_score, 2),
        'signature_score': round(signature_score, 2),
        'logo_score': round(logo_score, 2),
        'stamp_score': round(stamp_score_inverted, 2),
        'analysis_details': analysis_details,
    }


def get_risk_level(fraud_score):
    """
    Get risk level description based on fraud score.
    
    Args:
        fraud_score: Final fraud score (0-100)
        
    Returns:
        str: Risk level description
    """
    if fraud_score < 20:
        return "Very Low Risk"
    elif fraud_score < 40:
        return "Low Risk"
    elif fraud_score < 60:
        return "Medium Risk"
    elif fraud_score < 80:
        return "High Risk"
    else:
        return "Very High Risk"


def generate_recommendation(classification, fraud_score, analysis_details):
    """
    Generate recommendation based on analysis results.
    
    Args:
        classification: Fraud classification (genuine/suspicious/fraudulent)
        fraud_score: Final fraud score
        analysis_details: Detailed analysis dictionary
        
    Returns:
        str: Recommendation text
    """
    recommendations = []
    
    if classification == 'genuine':
        recommendations.append("This certificate appears to be genuine based on our AI analysis.")
        recommendations.append("All security features (text, signature, logo, stamp) appear valid.")
    
    elif classification == 'suspicious':
        recommendations.append("This certificate shows some suspicious characteristics.")
        
        # Check which components are suspicious
        text_score = analysis_details.get('text_analysis', {}).get('fraud_probability', 0)
        if text_score > 40:
            recommendations.append("- The text content shows some fraud indicators.")
        
        sig_score = analysis_details.get('signature_analysis', {}).get('fraud_indicator', 0)
        if sig_score > 40:
            recommendations.append("- The signature does not match expected patterns.")
        
        logo_score = analysis_details.get('logo_analysis', {}).get('fraud_indicator', 0)
        if logo_score > 40:
            recommendations.append("- The logo verification failed or shows anomalies.")
        
        stamp_score = analysis_details.get('stamp_analysis', {}).get('fraud_indicator', 0)
        if stamp_score > 40:
            recommendations.append("- The digital stamp verification shows issues.")
    
    else:  # fraudulent
        recommendations.append("WARNING: This certificate appears to be fraudulent!")
        recommendations.append("Multiple security features failed verification:")
        
        # Check all components
        text_score = analysis_details.get('text_analysis', {}).get('fraud_probability', 0)
        if text_score > 50:
            recommendations.append("- Text content contains fraud indicators")
        
        sig_score = analysis_details.get('signature_analysis', {}).get('fraud_indicator', 0)
        if sig_score > 50:
            recommendations.append("- Signature verification failed")
        
        logo_score = analysis_details.get('logo_analysis', {}).get('fraud_indicator', 0)
        if logo_score > 50:
            recommendations.append("- Logo verification failed")
        
        stamp_score = analysis_details.get('stamp_analysis', {}).get('fraud_indicator', 0)
        if stamp_score > 50:
            recommendations.append("- Digital stamp verification failed")
    
    # Add general recommendation
    if classification != 'genuine':
        recommendations.append("\nPlease verify this certificate through official channels before taking any action.")
    
    return "\n".join(recommendations)
