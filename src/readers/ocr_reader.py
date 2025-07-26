import os
import re
from difflib import SequenceMatcher
from typing import Tuple, Optional, Dict

import pytesseract
from PIL import Image, ImageDraw
from pdf2image import convert_from_path

from src.readers.base_reader import BoxReader
from src.logger import log


class OcrReader(BoxReader):
    def __init__(self, filename: str, debug_dir: str = "./debug_ocr", lang: str = "eng+deu"):
        self.filename = filename
        self.debug_dir = debug_dir
        self.lang = lang
        self._page_image_cache: Dict[int, Image.Image] = {}
        os.makedirs(self.debug_dir, exist_ok=True)

    def _get_page_image(self, page: int, dpi: int = 300) -> Image.Image:
        """
        Convert and cache a specific page of the PDF to an image.
        """
        if page not in self._page_image_cache:
            images = convert_from_path(self.filename, first_page=page + 1, last_page=page + 1, dpi=dpi)
            self._page_image_cache[page] = images[0]
        return self._page_image_cache[page]

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
            image = self._get_page_image(page)

            # Ensure box is within image bounds
            x0, y0, x1, y1 = map(int, box)
            x0 = max(0, x0)
            y0 = max(0, y0)
            x1 = min(image.width, x1)
            y1 = min(image.height, y1)

            cropped_image = image.crop(box)

            raw_text = pytesseract.image_to_string(
                cropped_image,
                lang=self.lang,
                config="--psm 6 --oem 1"
            ).strip()

            # Clean up line breaks and remove hyphenation artifacts
            cleaned_text = raw_text.replace("-\n", "").replace("\n", " ").strip()

            if not cleaned_text or len(cleaned_text) < 3 or not re.search(r'\w', cleaned_text):
                return None

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
            image = self._get_page_image(page)

            # OCR with bounding box data
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT,
                config="--psm 6"
            )

            search_normalized = search_text.lower().replace(" ", "").replace("-", "")

            valid_indices = [
                i for i, word in enumerate(data['text'])
                if word and word.strip() and int(data.get("conf", ["0"])[i]) > 50
            ]

            words = [
                data['text'][i].strip()
                for i in valid_indices
            ]

            normalized_words = [
                w.lower().replace(" ", "").replace("-", "") for w in words
            ]

            draw = ImageDraw.Draw(image)

            for idx, i in enumerate(valid_indices):
                for window in range(1, 4):  # Try 1- to 3-word combinations
                    if idx + window > len(valid_indices):
                        continue

                    j_indices = valid_indices[idx:idx + window]
                    joined = ''.join([normalized_words[k] for k in range(idx, idx + window)])

                    ratio = SequenceMatcher(None, joined, search_normalized).ratio()

                    if ratio > 0.9:
                        # Matching window found, calculate bounding box
                        x0 = min(data['left'][j] for j in j_indices) - tolerance
                        y0 = min(data['top'][j] for j in j_indices) - tolerance
                        x1 = max(data['left'][j] + data['width'][j] for j in j_indices) + tolerance
                        y1 = max(data['top'][j] + data['height'][j] for j in j_indices) + tolerance

                        draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=2)
                        debug_path = self._save_debug_image(image, self.filename, page + 1)

                        log(f"Fuzzy match '{search_text}' ≈ '{joined}' at {x0, y0, x1, y1}")
                        log(f"Saved debug image: {debug_path}")
                        return int(x0), int(y0), int(x1), int(y1)

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
