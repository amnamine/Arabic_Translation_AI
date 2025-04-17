# Import libraries
import fitz  # PyMuPDF
from googletrans import Translator
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import sys

# Set console encoding
sys.stdout.reconfigure(encoding='utf-8')

def translate_pdf():
    try:
        # Load PDF from local path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(current_dir, "1954.pdf")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File not found at {pdf_path}")
            return

        # Open and extract text
        doc = fitz.open(pdf_path)
        arabic_text = ""
        
        for page in doc:
            text = page.get_text()
            arabic_text += text + "\n"

        # Reshape Arabic text
        reshaped_text = arabic_reshaper.reshape(arabic_text)
        bidi_text = get_display(reshaped_text)

        # Print with encoding handling
        print("Original Arabic Text (Reshaped for Display):".encode('utf-8').decode('utf-8'))
        print(bidi_text.encode('utf-8').decode('utf-8'))

        # Translate text
        translator = Translator()
        translation_en = translator.translate(arabic_text, src='ar', dest='en')
        translation_fr = translator.translate(arabic_text, src='ar', dest='fr')

        print("\nEnglish Translation:".encode('utf-8').decode('utf-8'))
        print(translation_en.text.encode('utf-8').decode('utf-8'))

        print("\nFrench Translation:".encode('utf-8').decode('utf-8'))
        print(translation_fr.text.encode('utf-8').decode('utf-8'))
        
    except UnicodeEncodeError as ue:
        print("Encoding error occurred. Try running in a terminal with UTF-8 support.")
        print(f"Error details: {str(ue)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'doc' in locals():
            doc.close()

if __name__ == "__main__":
    translate_pdf()
