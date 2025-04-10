import fitz
from . import BaseExtractor

class TextExtractor(BaseExtractor):
    def extract(self, pdf_path: str) -> list[dict]:
        doc =  fitz.open(pdf_path)
        extracted = []

        for page_number, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")
            for block in blocks:
                
                if len(block) >= 5:
                    x0, y0, x1, y1, text = block[:5]
                else:
                    continue

                text = text.strip()
                if not text:
                    continue

                extracted.append({
                    "type": "text",
                    "content": text,
                    "bbox": [x0, y0, x1, y1],
                    "page": page_number
                })

        doc.close()
        return extracted