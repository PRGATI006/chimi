"""
Digital Stamp Verification Model using Hough Circle Transform
Detects and verifies circular stamps in certificates.
"""
import os
import cv2
import numpy as np
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class StampVerifier:
    """
    Verifies digital stamps in certificates using Hough Circle Transform.
    """
    
    def __init__(self):
        """Initialize the stamp verifier."""
        self.min_stamp_radius = 30
        self.max_stamp_radius = 150
    
    def preprocess_image(self, image):
        """Preprocess image for stamp detection."""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply bilateral filter to reduce noise while keeping edges
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(filtered)
        
        return enhanced, gray
    
    def detect_circles(self, image):
        """
        Detect circular shapes using Hough Circle Transform.
        
        Args:
            image: Preprocessed grayscale image
            
        Returns:
            List of detected circles
        """
        # Apply edge detection
        edges = cv2.Canny(image, 30, 100)
        
        # Dilate edges to connect broken circles
        kernel = np.ones((3, 3), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Hough Circle Transform
        circles = cv2.HoughCircles(
            dilated,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=self.min_stamp_radius,
            maxRadius=self.max_stamp_radius
        )
        
        detected_circles = []
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            for (x, y, r) in circles:
                detected_circles.append({
                    'center': (x, y),
                    'radius': r,
                    'area': np.pi * r * r
                })
        
        return detected_circles
    
    def verify_stamp_features(self, image, circle):
        """
        Verify if detected circle is likely a stamp.
        
        Args:
            image: Original image
            circle: Detected circle dictionary
            
        Returns:
            dict: Feature analysis results
        """
        x, y = circle['center']
        r = circle['radius']
        
        # Create mask for the circle
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (x, y), r, 255, -1)
        
        # Get region of interest
        roi = cv2.bitwise_and(image, image, mask=mask)
        
        # Analyze the region
        features = {}
        
        # Calculate mean intensity
        mean_intensity = np.mean(roi[mask > 0])
        features['mean_intensity'] = round(mean_intensity, 2)
        
        # Calculate circularity
        perimeter = 2 * np.pi * r
        # Approximate perimeter from contours would be better
        features['radius'] = r
        
        # Check for text-like patterns inside the circle
        # (using edge density as a proxy)
        edges = cv2.Canny(roi, 50, 150)
        edge_density = np.sum(edges > 0) / (np.pi * r * r)
        features['edge_density'] = round(edge_density, 4)
        
        # Determine if this looks like a stamp
        # Stamps typically have moderate edge density and specific size
        features['is_stamp_like'] = (
            0.05 < edge_density < 0.5 and
            self.min_stamp_radius * 1.5 < r < self.max_stamp_radius * 0.9
        )
        
        return features
    
    def detect_stamps(self, image_path):
        """
        Main detection method - analyzes certificate image for stamps.
        
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
                    'has_stamp': False,
                    'stamp_score': 0.0,
                    'confidence': 0.0,
                    'details': 'Could not read image',
                    'stamps_found': 0
                }
            
            # Preprocess
            enhanced, gray = self.preprocess_image(image)
            
            # Detect circles
            circles = self.detect_circles(enhanced)
            
            if not circles:
                return {
                    'has_stamp': False,
                    'stamp_score': 0.0,
                    'confidence': 0.0,
                    'details': 'No circular stamps detected',
                    'stamps_found': 0
                }
            
            # Analyze each detected circle
            stamp_candidates = []
            
            for circle in circles:
                features = self.verify_stamp_features(gray, circle)
                if features['is_stamp_like']:
                    stamp_candidates.append({
                        'circle': circle,
                        'features': features
                    })
            
            # Calculate stamp score based on findings
            if stamp_candidates:
                # Higher score for more stamp-like circles
                stamp_score = min(100, len(stamp_candidates) * 30 + 50)
                confidence = min(95, stamp_score + 10)
                
                return {
                    'has_stamp': True,
                    'stamp_score': round(stamp_score, 2),
                    'confidence': round(confidence, 2),
                    'details': f"Found {len(stamp_candidates)} stamp-like circular element(s)",
                    'stamps_found': len(stamp_candidates),
                    'candidates': stamp_candidates,
                    'method': 'hough_circles'
                }
            else:
                # Some circles found but not stamp-like
                return {
                    'has_stamp': False,
                    'stamp_score': round(len(circles) * 15, 2),
                    'confidence': round(len(circles) * 10, 2),
                    'details': f"Found {len(circles)} circular shapes but none stamp-like",
                    'stamps_found': len(circles),
                    'method': 'hough_circles'
                }
            
        except Exception as e:
            logger.error(f"Error in stamp verification: {e}")
            return {
                'has_stamp': False,
                'stamp_score': 0.0,
                'confidence': 0.0,
                'details': f'Error: {str(e)}',
                'stamps_found': 0
            }


def load_model():
    """Helper function to load the model globally."""
    global _stamp_verifier
    if '_stamp_verifier' not in globals():
        _stamp_verifier = StampVerifier()
    return _stamp_verifier
