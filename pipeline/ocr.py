import numpy as np
from PIL import Image


def run_ocr(image: Image.Image, reader) -> str:
    img_array = np.array(image.convert("RGB"))
    results = reader.readtext(img_array, detail=0, paragraph=True)
    return "\n".join(results)
