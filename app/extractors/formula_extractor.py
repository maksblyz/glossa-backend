from . import BaseExtractor
import fitz
import re

class FormulaExtractor(BaseExtractor):
    def extract(self, pdf_path: str) -> list[dict]:
        doc = fitz.open(pdf_path)
        extracted = []
        math_chars = re.compile(r"[∑∫∂∞≈≠≤≥⇔→←±√×÷≡^_{}|\\]")
        for page_number, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")
            for block in blocks:
                # only complete blocks
                if len(block) < 5:
                    continue
                x0, y0, x1, y1, text = block[:5]
                text = text.strip()

                # clean whitespace / empty blocks
                if not text:
                    continue

                if math_chars.search(text) or len(re.findall(r"[A-Za-z0-9]", text)) > 0 and "^" in text:
                    extracted.append({
                        "type": "formula",
                        "content": text,
                        "bbox": [x0, y0, x1, y1],
                        "page": page_number
                    })

        doc.close()
        return extracted


