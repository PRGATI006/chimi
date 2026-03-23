"""
Signature Detection Model using SSIM (Structural Similarity Index)
Compares uploaded certificate signatures with stored genuine signatures.
"""
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SignatureDetector:
    """
    Detects and verifies signatures in certificates using SSIM comparison.
    """
    
    def __init__(self, reference_signature_path=None):
        """
        Initialize the signature detector.
        
        Args:
            reference_signature_path: Path to reference genuine signature image
        """
        # Default paths for reference signatures
        self.reference_paths = [
            reference_signature_path,
            os.path.join(settings.MEDIA_ROOT, 'signatures', 'genuine_signature.png'),
            os.path.join(settings.MEDIA_ROOT, 'signatures', 'reference.png'),
            os.path.join(settings.BASE_DIR, 'fraud', 'static', 'signatures', 'reference.png'),
        ]
        
        # Try to find a valid reference signature
        self.reference_signature = None
        for path in self.reference_paths:
            if path and os.path.exists(path):
                try:
                    self.reference_signature = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                    if self.reference_signature is not None:
                        logger.info(f"Loaded reference signature from {path}")
                        break
                except Exception as e:
                    logger.warning(f"Could not load signature from {path}: {e}")
        
        # If no reference found, create a placeholder
        if self.reference_signature is None:
            logger.warning("No reference signature found. Using default detection.")
            self.reference_signature = self._create_default_signature()
    
    def _create_default_signature(self):
        """Create a default signature template for basic detection."""
        # Create a simple signature-like pattern
        signature = np.zeros((200, 400), dtype=np.uint8)
        cv2.putText(signature, 'SIGNATURE', (50, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255), 2)
        return signature
    
    def preprocess_image(self, image):
        """Preprocess image for signature detection."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Morphological operations to enhance signature-like regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return morph, gray
    
    def detect_signature_regions(self, image):
        """
        Detect potential signature regions in the certificate image.
        
        Args:
            image: Certificate image (numpy array)
            
        Returns:
            List of bounding boxes for potential signatures
        """
        morph, gray = self.preprocess_image(image)
        
        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        signature_regions = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter by aspect ratio and size (signatures are typically wide and short)
            aspect_ratio = w / max(h, 1)
            area = w * h
            
            # Signatures are usually between 10000 and 200000 pixels
            # and have aspect ratio between 2 and 10
            if 10000 < area < 300000 and 1.5 < aspect_ratio < 15:
                signature_regions.append({
                    'bbox': (x, y, w, h),
                    'aspect_ratio': aspect_ratio,
                    'area': area
                })
        
        return signature_regions
    
    def extract_signature(self, image, bbox):
        """Extract the signature region from the image."""
        x, y, w, h = bbox
        
        # Add some padding
        pad = 10
        x = max(0, x - pad)
        y = max(0, y - pad)
        w = min(image.shape[1] - x, w + 2 * pad)
        h = min(image.shape[0] - y, h + 2 * pad)
        
        # Extract region
        signature = image[y:y+h, x:x+w]
        
        # Resize to match reference
        if self.reference_signature is not None:
            signature = cv2.resize(signature, 
                                   (self.reference_signature.shape[1], 
                                    self.reference_signature.shape[0]))
        
        return signature
    
    def compare_signatures(self, detected_signature, reference_signature):
        """
        Compare detected signature with reference using SSIM.
        
        Args:
            detected_signature: Extracted signature from certificate
            reference_signature: Reference genuine signature
            
        Returns:
            float: Similarity score (0-100)
        """
        if detected_signature is None or reference_signature is None:
            return 0.0
        
        # Ensure same size
        if detected_signature.shape != reference_signature.shape:
            detected_signature = cv2.resize(
                detected_signature, 
                (reference_signature.shape[1], reference_signature.shape[0])
            )
        
        # Calculate SSIM
        similarity = ssim(detected_signature, reference_signature)
        
        # Convert to percentage (0-100)
        return round(similarity * 100, 2)
    
    def analyze_signature_features(self, signature_region):
        """Analyze features of detected signature region."""
        if signature_region is None:
            return {'has_signature': False, 'clarity': 0, 'completeness': 0}
        
        features = {}
        
        # Calculate pixel density (non-white pixels)
        non_white = np.sum(signature_region < 250)
        total_pixels = signature_region.size
        features['pixel_density'] = round(non_white / total_pixels, 4)
        
        # Calculate edge density (using Canny)
        edges = cv2.Canny(signature_region, 50, 150)
        edge_density = np.sum(edges > 0) / total_pixels
        features['edge_density'] = round(edge_density, 4)
        
        # Basic signature presence indicator
        features['has_signature'] = features['pixel_density'] > 0.05
        
        return features
    
    def detect(self, image_path):
        """
        Main detection method - analyzes certificate image for signatures.
        
        Args:
            image_path: Path to certificate image file
            
        Returns:
            dict: Detection results with scores
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return {
                    'has_signature': False,
                    'similarity_score': 0.0,
                    'confidence': 0.0,
                    'details': 'Could not read image',
                    'regions_found': 0
                }
            
            # Detect potential signature regions
            regions = self.detect_signature_regions(image)
            
            if not regions:
                return {
                    'has_signature': False,
                    'similarity_score': 0.0,
                    'confidence': 0.0,
                    'details': 'No signature regions detected',
                    'regions_found': 0
                }
            
            # Get the most likely signature region (largest area)
            best_region = max(regions, key=lambda r: r['area'])
            
            # Extract signature
            morph, gray = self.preprocess_image(image)
            signature = self.extract_signature(gray, best_region['bbox'])
            
            # Compare with reference
            similarity_score = self.compare_signatures(signature, self.reference_signature)
            
            # Analyze features
            features = self.analyze_signature_features(signature)
            
            # Calculate confidence based on multiple factors
            confidence = min(100, similarity_score + (features['pixel_density'] * 50))
            
            return {
                'has_signature': features['has_signature'],
                'similarity_score': similarity_score,
                'confidence': round(confidence, 2),
                'details': f"Found {len(regions)} potential signature region(s)",
                'regions_found': len(regions),
                'best_region': best_region,
                'features': features,
                'method': 'ssim_comparison'
            }
            
        except Exception as e:
            logger.error(f"Error in signature detection: {e}")
            return {
                'has_signature': False,
                'similarity_score': 0.0,
                'confidence': 0.0,
                'details': f'Error: {str(e)}',
                'regions_found': 0
            }


def load_model():
    """Helper function to load the model globally."""
    global _signature_detector
    if '_signature_detector' not in globals():
        _signature_detector = SignatureDetector()
    return _signature_detector
