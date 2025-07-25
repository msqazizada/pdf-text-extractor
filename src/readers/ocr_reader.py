import os
from difflib import SequenceMatcher
from typing import Tuple, Optional

import pytesseract
from PIL import ImageDraw
from pdf2image import convert_from_path

from src.readers.base_reader import BoxReader
from src.logger import log


class OcrReader(BoxReader):
    def __init__(self, filename: str, debug_dir: str = "./debug_ocr"):
        self.filename = filename
        self.debug_dir = debug_dir
        os.makedirs(self.debug_dir, exist_ok=True)

    def read_text_from_box(
            self,
            page: int,
            box: Tuple[int, int, int, int]
    ) -> Optional[str]:
        """
        Extracts text from a specific bounding box on a given PDF page using OCR.
        Handles multi-word text reliably by removing spaces/hyphens and returning
        both raw and normalized versions.
        :param page:
        :param box:
        :return:
        """
        try:
            images = convert_from_path(self.filename, first_page=page + 1, last_page=page + 1)
            image = images[0]
            cropped_image = image.crop(box)

            raw_text = pytesseract.image_to_string(cropped_image).strip()
            # Clean up line breaks and remove hyphenation artifacts
            cleaned_text = raw_text.replace("-\n", "").replace("\n", " ").strip()

            return cleaned_text
        except Exception as e:
            log(f"OCR error on box {box} (page {page + 1}): {e}")
            return None

    def find_text_coordinates(
            self,
            search_text: str,
            page: int = 0,
            tolerance: int = 1
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Finds coordinates of a (possibly multi-word) search string using OCR on a PDF page.
        Uses fuzzy matching and joins nearby words for better accuracy.
        Saves a debug image with a red rectangle if match is found.
        """
        try:
            # Convert the specific page to image
            images = convert_from_path(self.filename, first_page=page + 1, last_page=page + 1)
            image = images[0]

            # OCR with bounding box data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

            search_normalized = search_text.lower().replace(" ", "").replace("-", "")

            words = [data['text'][i].strip() for i in range(len(data['text']))]
            normalized_words = [
                w.lower().replace(" ", "").replace("-", "") for w in words
            ]

            draw = ImageDraw.Draw(image)

            for i in range(len(normalized_words)):
                for window in range(1, 4):  # Try 1- to 3-word combinations
                    if i + window > len(normalized_words):
                        continue

                    joined = ''.join(normalized_words[i:i + window])
                    ratio = SequenceMatcher(None, joined, search_normalized).ratio()

                    if ratio > 0.9:
                        # Matching window found, calculate bounding box
                        x0 = min(data['left'][i:i + window]) - tolerance
                        y0 = min(data['top'][i:i + window]) - tolerance
                        x1 = max([data['left'][j] + data['width'][j] for j in range(i, i + window)]) + tolerance
                        y1 = max([data['top'][j] + data['height'][j] for j in range(i, i + window)]) + tolerance

                        draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=2)
                        debug_path = self._save_debug_image(image, self.filename, page + 1)

                        log(f"Fuzzy match '{search_text}' ≈ '{joined}' at {x0, y0, x1, y1}")
                        log(f"Saved debug image: {debug_path}")
                        return x0, y0, x1, y1

            log(f"'{search_text}' not found on page {page + 1}")
            return None
        except Exception as e:
            log(f"Error finding coordinates: {e}")
            return None

    def _save_debug_image(self, image, pdf_path: str, page_number: int) -> str:
        """
        Saves a debug image with bounding boxes.
        """
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        debug_path = os.path.join(self.debug_dir, f"{filename}_page{page_number}_debug.png")
        image.save(debug_path)
        return debug_path
