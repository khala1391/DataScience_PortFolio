import fitz  # PyMuPDF
from PIL import Image


def pdf_to_images(pdf_bytes: bytes, dpi: int = 150) -> list[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n--- หน้าถัดไป ---\n".join(pages)


def is_scanned_pdf(pdf_bytes: bytes, min_chars: int = 50) -> bool:
    text = extract_text_from_pdf(pdf_bytes)
    return len(text.strip()) < min_chars
