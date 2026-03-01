import json
import glob
import os
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor

translator = GoogleTranslator(source='auto', target='ko')

def translate_text(text):
    if not text.strip():
        return text
    try:
        # Split into chunks if too long, deep_translator has a 5000 character limit per request
        if len(text) > 4500:
            parts = [text[i:i+4500] for i in range(0, len(text), 4500)]
            translated = [translator.translate(p) for p in parts]
            return "".join(translated)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def process_notebook(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        nb = json.load(f)
        
    changed = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'markdown':
            source = cell.get('source', [])
            if not source:
                continue
                
            # source can be a string or list of strings
            if isinstance(source, list):
                # Translate block by block or string by string
                # To keep formatting, let's translate the whole text block then split if needed
                # However, newlines in list need to be preserved
                text = "".join(source)
                translated = translate_text(text)
                
                # We can just put it back as a single string or split by newline
                # Putting back as list of lines with \n
                new_source = [line + '\n' for line in translated.split('\n')]
                # remove the last \n to match original behavior often
                if len(new_source) > 0 and new_source[-1].endswith('\n') and not text.endswith('\n'):
                    new_source[-1] = new_source[-1][:-1]
                    
                cell['source'] = new_source
                changed = True
            elif isinstance(source, str):
                cell['source'] = translate_text(source)
                changed = True

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        print(f"Saved translated {filepath}")

def main():
    notebooks = glob.glob('mybook/**/*.ipynb', recursive=True)
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_notebook, notebooks)

if __name__ == "__main__":
    main()
