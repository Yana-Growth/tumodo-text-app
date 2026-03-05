import pypdf
import re

file_path = "/Users/maltseva/Dropbox/Мой Mac (MacBook Air — Женушка)/Desktop/Tumodo/База знаний. Копирайтер/TRIVIO-guidebook (1).pdf"

def extract_colors(path):
    try:
        reader = pypdf.PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        # Regex for Hex codes
        hex_colors = set(re.findall(r'#[0-9a-fA-F]{6}', text))
        # Regex for common color mentions potentially
        
        print("Found Hex Colors:", hex_colors)
        print("First 2000 chars of text for manual check:")
        print(text[:2000])
    except Exception as e:
        print(f"Error: {e}")

extract_colors(file_path)
