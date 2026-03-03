"""
Utilities package for Certificate Fraud Detection.
"""
from .ocr import extract_text
from .fraud_score import calculate_overall_fraud_score, generate_json_report, generate_pdf_report

__all__ = [
    'extract_text',
    'calculate_overall_fraud_score',
    'generate_json_report',
    'generate_pdf_report'
]
