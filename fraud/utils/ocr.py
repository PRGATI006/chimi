"""
OCR Utility using pytesseract
Extracts text from certificate images and PDFs.
"""
import os
import logging
from PIL import Image
import pytesseract

# Try to import pdf2image, make it optional
try:
    from pdf2image import convert_from_bytes
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logging.warning("pdf2image not available. PDF text extraction will be limited.")

# Configure logging
logger = logging.getLogger(__name__)

# Configure tesseract path (Windows specific)
if os.name == "nt":
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break


def extract_text_from_image(image_path):
    """Extract text from an image file using Tesseract OCR."""
    try:
        image = Image.open(image_path)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(image, config=custom_config)
        text = clean_extracted_text(text)
        
        logger.info(f"Successfully extracted {len(text)} characters from {image_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from image {image_path}: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using pytesseract."""
    if not PDF2IMAGE_AVAILABLE:
        logger.warning("pdf2image not available. Cannot process PDF files.")
        return "PDF processing not available. Please install pdf2image and poppler."
    
    try:
        images = convert_from_bytes(open(pdf_path, "rb").read())
        full_text = []
        
        for i, image in enumerate(images):
            logger.info(f"Processing page {i + 1} of PDF")
            custom_config = r"--oem 3 --psm 6"
            text = pytesseract.image_to_string(image, config=custom_config)
            full_text.append(text)
        
        combined_text = "\n\n--- Page Break ---\n\n".join(full_text)
        combined_text = clean_extracted_text(combined_text)
        
        logger.info(f"Successfully extracted {len(combined_text)} characters from PDF {pdf_path}")
        return combined_text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
        return ""


def extract_text_from_file(file_path):
    """Extract text from any supported file (image or PDF)."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in [".pdf"]:
        return extract_text_from_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]:
        return extract_text_from_image(file_path)
    else:
        logger.warning(f"Unsupported file type: {ext}")
        return ""


def extract_text_from_pil_image(image):
    """Extract text from a PIL Image object."""
    try:
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        custom_config = r"--oem 3 --psm 6"
        text = pytesseract.image_to_string(image, config=custom_config)
        text = clean_extracted_text(text)
        
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PIL image: {e}")
        return ""


def clean_extracted_text(text):
    """Clean and normalize extracted text."""
    if not text:
        return ""
    
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    text = "\n".join(lines)
    text = text.replace("\x00", "")
    
    return text


def get_text_confidence(image_path):
    """Get confidence score for extracted text."""
    try:
        image = Image.open(image_path)
        
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        confidences = [int(conf) for conf in data["conf"] if conf != "-1"]
        
        if confidences:
            return sum(confidences) / len(confidences)
        return 0.0
    except Exception as e:
        logger.error(f"Error getting text confidence: {e}")
        return 0.0
