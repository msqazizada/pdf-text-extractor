from typing import Tuple, List, Optional, Literal, Union

import pdfplumber
from pdfplumber import PDF

from src.match_strategy import MatchStrategy
from src.readers.ocr_reader import OcrReader
from src.readers.pdf_reader import PdfReader
from src.logger import log


class DataExtractor:
    def __init__(self, filename: str):
        """
        Initialize the DataExtractor with a file to process.

        Args:
            filename: Path to the PDF file to extract data from
        """
        self.filename = filename
        self._cached_pdf = None  # Cache the PDF object for multiple operations

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self.close()

    def close(self):
        """Close any open resources."""
        if self._cached_pdf is not None:
            self._cached_pdf.close()
            self._cached_pdf = None

    def _get_pdf(self) -> PDF:
        """Get the PDF object, using cached version if available."""
        if self._cached_pdf is None:
            try:
                self._cached_pdf = pdfplumber.open(self.filename)
            except Exception as e:
                log(f"Failed to open PDF file {self.filename}: {e}")
                raise
        return self._cached_pdf

    def _is_page_readable(self, page: int) -> bool:
        """
        Check if a page contains extractable text.

        Args:
            page: Zero-based page index

        Returns:
            bool: True if page contains extractable text, False otherwise
        """
        try:
            pdf = self._get_pdf()
            if page >= len(pdf.pages):
                log(f"Page {page + 1} is out of range (total pages: {len(pdf.pages)})")
                return False

            text = pdf.pages[page].extract_text()
            if not text or text.strip() == "":
                return False

            # Add more checks here: if it’s all whitespace or short garbage text
            cleaned = text.strip().replace("\n", "").replace(" ", "")
            if len(cleaned) < 10:  # Threshold: too little usable text
                return False

            return True
        except Exception as e:
            log(f"Failed to check readability on page {page + 1}: {e}")
            return False

    def get_best_reader(self, page: int) -> Union[PdfReader, OcrReader]:
        """
        Determine the best reader for a given page (PDF or OCR).

        Args:
            page: Zero-based page index

        Returns:
            A reader instance (PdfReader or OcrReader)
        """
        try:
            if self._is_page_readable(page):
                log(f"Using PdfReader for page {page + 1} of {self.filename}")
                return PdfReader(self.filename)
            else:
                log(f"Falling back to OcrReader for page {page + 1} of {self.filename}")
        except Exception as e:
            log(f"Error determining best reader for page {page + 1}, falling back to OCR: {e}")
        return OcrReader(self.filename)

    def extract_text(
            self,
            page: int,
            boxes: List[Tuple[int, int, int, int]],
            match_strategy: Optional[MatchStrategy] = None,
            fallback: str = "-"
    ) -> str:
        """
        Extract text from specified boxes on a page using the appropriate reader.

        Args:
            page: Zero-based page index
            boxes: List of bounding boxes (x0, y0, x1, y1) to try
            match_strategy: Optional strategy to validate extracted text
            fallback: Default value to return if no text is found

        Returns:
            Extracted text that matches criteria, or fallback value if none found
        """
        if not boxes:
            return fallback

        reader = None
        try:
            reader = self.get_best_reader(page)

            for box in boxes:
                try:
                    text = reader.read_text_from_box(page, box)
                    # if text and (not match_strategy or match_strategy.matches(text)):
                    return text.strip()
                except Exception as e:
                    log(f"Failed to read from box {box} on page {page + 1}: {e}")
                    continue

        except Exception as e:
            log(f"Error during text extraction on page {page + 1}: {e}")
        finally:
            if hasattr(reader, 'close'):
                reader.close()

        return fallback
