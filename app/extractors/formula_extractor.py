import fitz
import re
from . import BaseExtractor

class FormulaExtractor(BaseExtractor):
    def __init__(self):
        # include extra math symbols including ✓ and ̂
        self.math_chars = re.compile(r"[✓̂∑∫∂∞≈≠≤≥⇔→←±√×÷≡^_{}|\\=\+\-\*/]")
        self.words = re.compile(r"\b[a-zA-Z]{3,}\b")

    def is_formula_like(self, text: str) -> bool:
        if not (5 <= len(text) <= 300):
            return False
        if not self.math_chars.search(text):
            return False

        word_count = len(self.words.findall(text))
        symbol_count = len(re.findall(r"[=+\-\*/^_]", text))
        # allow a few words but ensure formulas have enough math ops;
        # if word_count is more than twice the symbol_count, reject.
        if symbol_count < 1 or (word_count > 0 and word_count >= 2 * symbol_count):
            return False
        return True

    def merge_formula_blocks(self, formulas, vertical_tol=5, horizontal_overlap_threshold=0.2):
        # group by page
        formulas_by_page = {}
        for formula in formulas:
            page = formula["page"]
            formulas_by_page.setdefault(page, []).append(formula)

        merged_results = []
        for page, blocks in formulas_by_page.items():
            # sort blocks by vertical then horizontal position
            blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
            merged = []
            for block in blocks:
                if merged:
                    prev = merged[-1]
                    # check if current block is vertically close to previous one
                    if block["bbox"][1] <= prev["bbox"][3] + vertical_tol:
                        # calculate horizontal overlap
                        prev_x0, _, prev_x1, _ = prev["bbox"]
                        curr_x0, _, curr_x1, _ = block["bbox"]
                        overlap = max(0, min(prev_x1, curr_x1) - max(prev_x0, curr_x0))
                        min_width = min(prev_x1 - prev_x0, curr_x1 - curr_x0)
                        if min_width > 0 and (overlap / min_width) > horizontal_overlap_threshold:
                            new_bbox = [
                                min(prev["bbox"][0], block["bbox"][0]),
                                min(prev["bbox"][1], block["bbox"][1]),
                                max(prev["bbox"][2], block["bbox"][2]),
                                max(prev["bbox"][3], block["bbox"][3])
                            ]
                            merged[-1] = {
                                "type": "formula",
                                "content": prev["content"] + "\n" + block["content"],
                                "bbox": new_bbox,
                                "page": page
                            }
                            continue
                merged.append(block)
            merged_results.extend(merged)
        return merged_results

    def merge_line_blocks(self, blocks, y_tol=3, x_gap=10):
        # groups blocks that are on the same horizontal line
        blocks = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))
        merged = []
        if not blocks:
            return merged
        current_line = [blocks[0]]

        def same_line(b1, b2):
            top1, bottom1 = b1["bbox"][1], b1["bbox"][3]
            top2, bottom2 = b2["bbox"][1], b2["bbox"][3]
            return not (bottom1 < top2 - y_tol or bottom2 < top1 - y_tol)

        for b in blocks[1:]:
            last = current_line[-1]
            if same_line(last, b):
                gap = b["bbox"][0] - last["bbox"][2]
                if gap < x_gap:
                    new_bbox = [
                        min(last["bbox"][0], b["bbox"][0]),
                        min(last["bbox"][1], b["bbox"][1]),
                        max(last["bbox"][2], b["bbox"][2]),
                        max(last["bbox"][3], b["bbox"][3])
                    ]
                    current_line[-1] = {
                        "type": "formula",
                        "content": last["content"] + " " + b["content"],
                        "bbox": new_bbox,
                        "page": b["page"]
                    }
                else:
                    current_line.append(b)
            else:
                merged.extend(current_line)
                current_line = [b]
        merged.extend(current_line)
        return merged

    def extract(self, pdf_path: str) -> list[dict]:
        doc = fitz.open(pdf_path)
        extracted = []

        for page_number, page in enumerate(doc, start=1):
            blocks = page.get_text("blocks")
            for block in blocks:
                if len(block) < 5:
                    continue
                x0, y0, x1, y1, text = block[:5]
                text = text.strip()
                if not text:
                    continue
                if self.is_formula_like(text):
                    extracted.append({
                        "type": "formula",
                        "content": text,
                        "bbox": [x0, y0, x1, y1],
                        "page": page_number
                    })
        doc.close()
        # first merge vertically overlapping blocks
        merged = self.merge_formula_blocks(extracted)
        # then merge horizontally adjacent blocks on the same line
        final = self.merge_line_blocks(merged)
        return final
