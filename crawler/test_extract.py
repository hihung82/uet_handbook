import sys
sys.stdout.reconfigure(encoding='utf-8')

from extractor import extract_text


url = "https://handbook.uet.vnu.edu.vn"

text = extract_text(url)

print(text[:2000])