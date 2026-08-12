import fitz  # PyMuPDF

doc = fitz.open("Attention is all you need.pdf")

print("Pages:", len(doc))

for i, page in enumerate(doc):
    text = page.get_text("text")
    print(i, len(text))