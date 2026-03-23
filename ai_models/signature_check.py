"""
Signature verification using SSIM (Structural Similarity Index).
Lightweight and CPU-friendly approach.
"""
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

class SignatureChecker:
    """
    Signature detection and verification using SSIM.
    Uses image processing techniques instead of CNN for CPU efficiency.
    """
    
    def __init__(self):
        """Initialize the signature checker."""
        self.reference_signature_path = os.path.join('static', 'signatures', 'reference.png')
        
    def preprocess_image(self, image_path):
        """
        Preprocess image for signature detection.
        Converts to grayscale and applies thresholding.
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            return thresh
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def detect_signature_regions(self, processed_img):
        """
        Detect potential signature regions in the certificate.
        Returns list of bounding boxes.
        """
        try:
            # Find contours
            contours, _ = cv2.findContours(
                processed_img, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by size (signatures are typically medium-sized)
            signature_regions = []
            min_area = 1000
            max_area = 50000
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    # Check aspect ratio (signatures are usually wider than tall)
                    if w > h and w / h > 1.5:
                        signature_regions.append((x, y, w, h))
            
            return signature_regions
        except Exception as e:
            print(f"Error detecting signature regions: {e}")
            return []
    
    def detect_signature(self, image_path):
        """
        Detect if a signature is present in the certificate.
        Returns True if signature detected, False otherwise.
        """
        try:
            processed = self.preprocess_image(image_path)
            if processed is None:
                return False
            
            regions = self.detect_signature_regions(processed)
            
            # If we found potential signature regions
            return len(regions) > 0
            
        except Exception as e:
            print(f"Error in signature detection: {e}")
            return False
    
    def compare_signatures(self, signature1_path, signature2_path=None):
        """
        Compare two signatures using SSIM.
        Returns similarity score between 0.0 and 1.0.
        """
        try:
            # Use reference signature if second path not provided
            if signature2_path is None:
                signature2_path = self.reference_signature_path
            
            # Check if reference exists
            if not os.path.exists(signature2_path):
                print(f"Reference signature not found at {signature2_path}")
                return 0.5  # Neutral score if no reference
            
            # Preprocess both images
            img1 = self.preprocess_image(signature1_path)
            img2 = self.preprocess_image(signature2_path)
            
            if img1 is None or img2 is None:
                return 0.5
            
            # Resize to same dimensions if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Calculate SSIM
            score, _ = ssim(img1, img2, full=True)
            
            # SSIM returns -1 to 1, convert to 0 to 1
            return (score + 1) / 2
            
        except Exception as e:
            print(f"Error comparing signatures: {e}")
            return 0.5
    
    def analyze_signature(self, certificate_path):
        """
        Full signature analysis for a certificate.
        Returns dict with detection status and fraud score.
        """
        result = {
            'detected': False,
            'fraud_score': 0.8,  # Default high fraud score if no signature
            'details': 'No signature analysis performed'
        }
        
        try:
            # Check if signature is detected
            detected = self.detect_signature(certificate_path)
            result['detected'] = detected
            
            if detected:
                # If detected, try to compare with reference
                similarity = self.compare_signatures(certificate_path)
                
                # Higher similarity = lower fraud score
                result['fraud_score'] = 1.0 - similarity
                result['details'] = f"Signature detected, similarity: {similarity:.2f}"
            else:
                result['fraud_score'] = 0.9  # High fraud score if no signature
                result['details'] = 'No signature detected in certificate'
                
        except Exception as e:
            print(f"Error in signature analysis: {e}")
            result['fraud_score'] = 0.5  # Neutral score on error
        
        return result


# Global instance
_signature_checker = None

def get_signature_checker():
    """Get or create the signature checker instance."""
    global _signature_checker
    if _signature_checker is None:
        _signature_checker = SignatureChecker()
    return _signature_checker
