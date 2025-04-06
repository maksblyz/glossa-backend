import fitz

def test_pymupdf():
    doc = fitz.open("Glossa_Paper.pdf")
    for page in doc:
        blocks = page.get_text("blocks")
        print(blocks)

if __name__ == "__main__":
    test_pymupdf()