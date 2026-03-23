"""
OCR utility for extracting text from images and PDFs.
Uses pytesseract for text extraction.
"""
import os
import warnings
warnings.filterwarnings('ignore')

# Try to configure Tesseract path
try:
    import pytesseract
    
    # Try common Tesseract installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
except Exception as e:
    print(f"Warning: Tesseract configuration error: {e}")

from PIL import Image
import pytesseract


def extract_text_from_image(image_path):
    """
    Extract text from an image file using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text as string
    """
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            return ""
        
        # Open image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Extract text using pytesseract
        text = pytesseract.image_to_string(img)
        
        return text.strip()
        
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    First converts PDF pages to images, then uses OCR.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            return ""
        
        # Try using pdf2image if available
        try:
            from pdf2image import convert_from_path
            
            images = convert_from_path(pdf_path)
            full_text = ""
            
            for page_num, image in enumerate(images):
                # Save temporary image
                temp_path = f'temp_page_{page_num}.png'
                image.save(temp_path, 'PNG')
                
                # Extract text from image
                text = extract_text_from_image(temp_path)
                full_text += text + "\n"
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            return full_text.strip()
            
        except ImportError:
            print("pdf2image not installed. Using fallback method.")
            # Fallback: Try to extract text directly
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
                    return text.strip()
            except ImportError:
                print("PyPDF2 not installed. Returning empty text.")
                return ""
            except Exception as e:
                print(f"Error reading PDF: {e}")
                return ""
                
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""


def extract_text(file_path):
    """
    Extract text from any supported file (image or PDF).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text as string
    """
    if not os.path.exists(file_path):
        return ""
    
    # Get file extension
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
        return extract_text_from_image(file_path)
    elif ext == '.pdf':
        return extract_text_from_pdf(file_path)
    else:
        print(f"Unsupported file type: {ext}")
        return ""
