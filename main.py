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

def main():
    extractor = FormulaExtractor()
    results = extractor.extract("glasso_table.pdf")
    print(f"Extracted {len(results)} formulas")
    for f in results:
        print(f)

if __name__ == "__main__":
    main()