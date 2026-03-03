"""
Logo detection using OpenCV template matching.
Lightweight and CPU-friendly approach.
"""
import os
import cv2
import numpy as np

class LogoChecker:
    """
    Logo detection and verification using OpenCV template matching.
    Uses template matching instead of CNN for CPU efficiency.
    """
    
    def __init__(self):
        """Initialize the logo checker."""
        self.reference_logo_path = os.path.join('static', 'logos', 'reference.png')
        
    def preprocess_image(self, image_path):
        """
        Preprocess image for logo detection.
        Converts to grayscale.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            return gray
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def detect_logo_regions(self, image_path):
        """
        Detect potential logo regions in the certificate.
        Uses edge detection and contour analysis.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply Canny edge detection
            edges = cv2.Canny(blur, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter contours by size and shape (logos are typically rectangular/square)
            logo_regions = []
            min_area = 500
            max_area = 50000
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area < area < max_area:
                    # Check if it's approximately rectangular
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.04 * peri, True)
                    
                    # If it has 4 corners, it's likely a logo or signature area
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = float(w) / h
                        # Logos are usually not too elongated
                        if 0.5 < aspect_ratio < 2.0:
                            logo_regions.append((x, y, w, h))
            
            return logo_regions
        except Exception as e:
            print(f"Error detecting logo regions: {e}")
            return []
    
    def detect_logo(self, image_path):
        """
        Detect if a logo is present in the certificate.
        Returns True if logo detected, False otherwise.
        """
        try:
            regions = self.detect_logo_regions(image_path)
            return len(regions) > 0
        except Exception as e:
            print(f"Error in logo detection: {e}")
            return False
    
    def compare_logos(self, logo_path, reference_path=None):
        """
        Compare detected logo with reference using template matching.
        Returns similarity score between 0.0 and 1.0.
        """
        try:
            # Use reference logo if path not provided
            if reference_path is None:
                reference_path = self.reference_logo_path
            
            # Check if reference exists
            if not os.path.exists(reference_path):
                print(f"Reference logo not found at {reference_path}")
                return 0.5
            
            # Preprocess images
            img = self.preprocess_image(logo_path)
            template = self.preprocess_image(reference_path)
            
            if img is None or template is None:
                return 0.5
            
            # Resize template to match image dimensions if needed
            if img.shape[1] < template.shape[1] or img.shape[0] < template.shape[0]:
                # If image is smaller than template, resize template
                scale = min(img.shape[1] / template.shape[1], 
                           img.shape[0] / template.shape[0])
                new_width = int(template.shape[1] * scale)
                new_height = int(template.shape[0] * scale)
                template = cv2.resize(template, (new_width, new_height))
            
            # Template matching using TM_CCOEFF_NORMED
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            # Convert to 0-1 range (higher match = higher similarity)
            return max_val
            
        except Exception as e:
            print(f"Error comparing logos: {e}")
            return 0.5
    
    def analyze_logo(self, certificate_path):
        """
        Full logo analysis for a certificate.
        Returns dict with detection status and fraud score.
        """
        result = {
            'detected': False,
            'fraud_score': 0.8,
            'details': 'No logo analysis performed'
        }
        
        try:
            # Check if logo is detected
            detected = self.detect_logo(certificate_path)
            result['detected'] = detected
            
            if detected:
                # If detected, try to compare with reference
                similarity = self.compare_logos(certificate_path)
                
                # Higher similarity = lower fraud score
                result['fraud_score'] = 1.0 - similarity
                result['details'] = f"Logo detected, similarity: {similarity:.2f}"
            else:
                result['fraud_score'] = 0.9  # High fraud score if no logo
                result['details'] = 'No logo detected in certificate'
                
        except Exception as e:
            print(f"Error in logo analysis: {e}")
            result['fraud_score'] = 0.5
        
        return result


# Global instance
_logo_checker = None

def get_logo_checker():
    """Get or create the logo checker instance."""
    global _logo_checker
    if _logo_checker is None:
        _logo_checker = LogoChecker()
    return _logo_checker
