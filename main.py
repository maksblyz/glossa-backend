import fitz
from app.extractors.text_extractor import TextExtractor
from app.extractors.table_extractor import TableExtractor
from app.extractors.image_extractor import ImageExtractor
from app.extractors.formula_extractor import FormulaExtractor

def test_pymupdf():
    doc = fitz.open("Glossa_Paper.pdf")
    for page in doc:
        blocks = page.get_text("blocks")
        print(blocks)

def visualize_sentences(pdf_path, sentence_data, out_path="output.pdf"):
    doc = fitz.open(pdf_path)
    for item in sentence_data:
        page = doc[item["page"] - 1]
        bbox = item["bbox"]

        # basic validation
        if not bbox or len(bbox) != 4:
            continue
        x0, y0, x1, y1 = bbox
        if not all(map(float, [x0, y0, x1, y1])):
            continue
        if abs(x1 - x0) < 1 or abs(y1 - y0) < 1:
            continue

        # skip footers
        if any(s in item["content"].lower() for s in ["author", "license", "mit press"]):
            continue

        rect = fitz.Rect(*bbox)
        page.draw_rect(rect, color=(1, 0, 0), width=0.5)

        # truncating text overlays
        text = item["content"]
        if len(text) > 60:
            text = text[:57] + "..."
        
        # proportional fontsize
        height = rect.y1 - rect.y0
        fontsize = max(3, min(6, height * 0.2))
        try:
            page.insert_textbox(rect, item["content"], fontsize=fontsize, color=(0, 0, 1))
        except Exception as e:
            print(f"Skipping textbox draw error: {e}")


    doc.save(out_path)


def main():
    extractor = TextExtractor()
    results = extractor.extract("glasso_sample.pdf")
    visualize_sentences("glasso_sample.pdf", results, "highlighted.pdf")

    print(f"Extracted {len(results)} text")
    for f in results:
        print(f)

if __name__ == "__main__":
    main()