"""
Stamp verification using Hough Circle Transform.
Lightweight and CPU-friendly approach.
"""
import os
import cv2
import numpy as np

class StampChecker:
    """
    Digital stamp verification using Hough Circle Transform.
    Uses image processing techniques instead of CNN for CPU efficiency.
    """
    
    def __init__(self):
        """Initialize the stamp checker."""
        self.reference_stamp_path = os.path.join('static', 'signatures', 'stamp_reference.png')
        
    def preprocess_image(self, image_path):
        """
        Preprocess image for stamp detection.
        Converts to grayscale and applies thresholding.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None, None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blur = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Apply Hough Circle detection on blurred image
            circles = cv2.HoughCircles(
                blur, 
                cv2.HOUGH_GRADIENT, 
                dp=1.2, 
                minDist=50,
                param1=50,
                param2=30,
                minRadius=20,
                maxRadius=100
            )
            
            return gray, circles
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None, None
    
    def detect_stamp(self, image_path):
        """
        Detect if a stamp is present in the certificate.
        Uses Hough Circle Transform to find circular patterns.
        Returns True if stamp detected, False otherwise.
        """
        try:
            gray, circles = self.preprocess_image(image_path)
            
            if circles is None:
                return False
            
            # Check if any circles were detected
            num_circles = circles.shape[1]
            return num_circles > 0
            
        except Exception as e:
            print(f"Error in stamp detection: {e}")
            return False
    
    def extract_stamp_regions(self, image_path):
        """
        Extract potential stamp regions from the certificate.
        Returns list of stamp bounding boxes.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []
            
            gray, circles = self.preprocess_image(image_path)
            
            if circles is None:
                return []
            
            stamp_regions = []
            height, width = gray.shape
            
            # Convert circles to integer
            circles = np.round(circles[0, :]).astype("int")
            
            for (x, y, r) in circles:
                # Calculate bounding box
                x1 = max(0, x - r)
                y1 = max(0, y - r)
                x2 = min(width, x + r)
                y2 = min(height, y + r)
                stamp_regions.append((x1, y1, x2 - x1, y2 - y1))
            
            return stamp_regions
        except Exception as e:
            print(f"Error extracting stamp regions: {e}")
            return []
    
    def analyze_stamp(self, certificate_path):
        """
        Full stamp analysis for a certificate.
        Returns dict with detection status and authenticity score.
        """
        result = {
            'detected': False,
            'authenticity_score': 0.5,
            'details': 'No stamp analysis performed',
            'num_circles': 0
        }
        
        try:
            # Check if stamp is detected
            detected = self.detect_stamp(certificate_path)
            result['detected'] = detected
            
            if detected:
                # Get stamp regions
                regions = self.extract_stamp_regions(certificate_path)
                result['num_circles'] = len(regions)
                
                # More circles typically means more likely to be a genuine stamp
                # Single clear circle = likely official stamp
                if len(regions) == 1:
                    result['authenticity_score'] = 0.8
                    result['details'] = 'Single stamp circle detected'
                elif len(regions) > 1:
                    result['authenticity_score'] = 0.6
                    result['details'] = f'{len(regions)} stamp circles detected'
                else:
                    result['authenticity_score'] = 0.5
                    result['details'] = 'Multiple stamp regions detected'
            else:
                result['authenticity_score'] = 0.9  # High score = likely fake (no stamp)
                result['details'] = 'No stamp detected in certificate'
                
        except Exception as e:
            print(f"Error in stamp analysis: {e}")
            result['authenticity_score'] = 0.5
        
        # Convert authenticity to fraud score (inverse)
        result['fraud_score'] = 1.0 - result['authenticity_score']
        
        return result


# Global instance
_stamp_checker = None

def get_stamp_checker():
    """Get or create the stamp checker instance."""
    global _stamp_checker
    if _stamp_checker is None:
        _stamp_checker = StampChecker()
    return _stamp_checker
