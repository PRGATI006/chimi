"""
Logo Detection Model using OpenCV Template Matching
Compares uploaded certificate logos with stored official logos.
"""
import os
import cv2
import numpy as np
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class LogoDetector:
    """
    Detects and verifies official logos in certificates using template matching.
    """
    
    def __init__(self, reference_logo_paths=None):
        """
        Initialize the logo detector.
        
        Args:
            reference_logo_paths: List of paths to reference official logo images
        """
        # Default paths for reference logos
        default_paths = [
            os.path.join(settings.MEDIA_ROOT, 'logos', 'official_logo.png'),
            os.path.join(settings.MEDIA_ROOT, 'logos', 'logo.png'),
            os.path.join(settings.BASE_DIR, 'fraud', 'static', 'logos', 'official.png'),
        ]
        
        if reference_logo_paths:
            default_paths = reference_logo_paths + default_paths
        
        # Try to find valid reference logos
        self.reference_logos = []
        for path in default_paths:
            if path and os.path.exists(path):
                try:
                    logo = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    if logo is not None:
                        self.reference_logos.append({
                            'image': logo,
                            'path': path,
                            'name': os.path.basename(path)
                        })
                        logger.info(f"Loaded reference logo from {path}")
                except Exception as e:
                    logger.warning(f"Could not load logo from {path}: {e}")
        
        # If no logos found, create a placeholder
        if not self.reference_logos:
            logger.warning("No reference logos found. Using default detection.")
            self.reference_logos.append({
                'image': self._create_default_logo(),
                'path': None,
                'name': 'default'
            })
    
    def _create_default_logo(self):
        """Create a default logo template."""
        logo = np.zeros((100, 100), dtype=np.uint8)
        cv2.rectangle(logo, (10, 10), (90, 90), (255), 2)
        cv2.circle(logo, (50, 50), 30, (255), 2)
        return logo
    
    def preprocess_image(self, image):
        """Preprocess image for logo detection."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        return blurred
    
    def template_match(self, image, template):
        """
        Perform template matching to find logo in image.
        
        Args:
            image: Certificate image (grayscale)
            template: Logo template (grayscale)
            
        Returns:
            dict: Match results with best match location and confidence
        """
        # Resize template to multiple scales for scale-invariant matching
        best_match = None
        best_confidence = 0
        best_location = None
        
        # Try multiple scales
        scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        
        for scale in scales:
            # Resize template
            new_width = int(template.shape[1] * scale)
            new_height = int(template.shape[0] * scale)
            
            if new_width < 20 or new_height < 20:
                continue
            if new_width > image.shape[1] or new_height > image.shape[0]:
                continue
                
            resized_template = cv2.resize(template, (new_width, new_height))
            
            # Template matching
            result = cv2.matchTemplate(image, resized_template, cv2.TM_CCOEFF_NORMED)
            
            # Find best match in result
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_confidence:
                best_confidence = max_val
                best_match = resized_template
                best_location = max_loc
        
        return {
            'confidence': best_confidence,
            'location': best_location,
            'matched_template': best_match,
            'template_size': best_match.shape if best_match is not None else None
        }
    
    def detect_logo_regions(self, image):
        """
        Detect potential logo regions in the certificate image.
        
        Args:
            image: Certificate image
            
        Returns:
            List of bounding boxes for potential logos
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        logo_regions = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            
            # Logos are typically square or rectangular, between certain sizes
            aspect_ratio = w / max(h, 1)
            
            if 1000 < area < 100000 and 0.5 < aspect_ratio < 2.0:
                logo_regions.append({
                    'bbox': (x, y, w, h),
                    'aspect_ratio': aspect_ratio,
                    'area': area
                })
        
        return logo_regions
    
    def verify_logo(self, image_path):
        """
        Main verification method - analyzes certificate image for official logos.
        
        Args:
            image_path: Path to certificate image file
            
        Returns:
            dict: Verification results with scores
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'has_logo': False,
                    'similarity_score': 0.0,
                    'confidence': 0.0,
                    'details': 'Could not read image',
                    'method': 'template_matching'
                }
            
            # Preprocess
            gray = self.preprocess_image(image)
            
            best_score = 0
            best_logo_name = None
            
            # Try matching with each reference logo
            for ref_logo in self.reference_logos:
                result = self.template_match(gray, ref_logo['image'])
                
                if result['confidence'] > best_score:
                    best_score = result['confidence']
                    best_logo_name = ref_logo['name']
            
            # Convert confidence to similarity score (0-100)
            similarity_score = round(best_score * 100, 2)
            
            # Determine if logo is present
            has_logo = similarity_score > 30  # Threshold for detection
            
            return {
                'has_logo': has_logo,
                'similarity_score': similarity_score,
                'confidence': similarity_score,
                'details': f"{'Official logo detected' if has_logo else 'No official logo found'} (best match: {best_logo_name})",
                'best_match': best_logo_name,
                'method': 'template_matching'
            }
            
        except Exception as e:
            logger.error(f"Error in logo detection: {e}")
            return {
                'has_logo': False,
                'similarity_score': 0.0,
                'confidence': 0.0,
                'details': f'Error: {str(e)}',
                'method': 'template_matching'
            }


def load_model():
    """Helper function to load the model globally."""
    global _logo_detector
    if '_logo_detector' not in globals():
        _logo_detector = LogoDetector()
    return _logo_detector
