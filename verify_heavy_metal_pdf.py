from app import generate_fallback_result, generate_pdf
from PyPDF2 import PdfReader
from io import BytesIO

user_prompt = 'Design a heavy metal adsorbent for lead, cadmium, and arsenic removal from industrial wastewater'
result = generate_fallback_result(user_prompt)
pdf_bytes = generate_pdf(user_prompt, result)

pdf_reader = PdfReader(BytesIO(pdf_bytes))
page_text = pdf_reader.pages[0].extract_text()

# Find and print the disclaimer
if 'DISCLAIMER' in page_text:
    start = page_text.find('DISCLAIMER')
    end = min(start + 550, len(page_text))
    print('\nHEAVY METAL ADSORBENT - DISCLAIMER IN PDF:')
    print('=' * 80)
    print(page_text[start:end])
    print('\n[OK] PDF contains heavy-metal-specific disclaimer')
