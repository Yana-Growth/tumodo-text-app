import os
import pandas as pd
import json

def extract_text_from_pdf(file_path):
    text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except ImportError:
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except ImportError:
            return "Error: Neither pypdf nor PyPDF2 is installed."
        except Exception as e:
            return f"Error reading PDF with PyPDF2: {e}"
    except Exception as e:
        return f"Error reading PDF with pypdf: {e}"
    return text

def extract_text_from_excel(file_path):
    try:
        xls = pd.ExcelFile(file_path)
        text = ""
        for sheet_name in xls.sheet_names:
            text += f"--- Sheet: {sheet_name} ---\n"
            df = xls.parse(sheet_name)
            text += df.to_string() + "\n"
        return text
    except Exception as e:
        return f"Error reading Excel file: {e}"

files_to_process = {
    "guidebook": "/Users/maltseva/Dropbox/Мой Mac (MacBook Air — Женушка)/Desktop/Tumodo/База знаний. Копирайтер/TRIVIO-guidebook (1).pdf",
    "facebook_ads": "/Users/maltseva/Dropbox/Мой Mac (MacBook Air — Женушка)/Desktop/Tumodo/База знаний. Копирайтер/Тексты объявлений FB.pdf",
    "audience_portrait": "/Users/maltseva/Dropbox/Мой Mac (MacBook Air — Женушка)/Desktop/Tumodo/База знаний. Копирайтер/Портрет целевой аудитории новый (3).xlsx"
}

results = {}
for key, path in files_to_process.items():
    if os.path.exists(path):
        if path.endswith('.pdf'):
            results[key] = extract_text_from_pdf(path)
        elif path.endswith('.xlsx'):
            results[key] = extract_text_from_excel(path)
    else:
        results[key] = f"File not found: {path}"

# Print results in a way we can capture
for key, content in results.items():
    print(f"=== {key} ===")
    print(content[:5000]) # Limit output per file to avoid huge logs if not needed, but we need enough to analyze
    print("\n")
