import csv
import os
from typing import Tuple, Optional, List

import pdfplumber

from src.readers.base_reader import BoxReader
from src.logger import log


class PdfReader(BoxReader):
    def __init__(self, filename: str):
        self.filename = filename

    def read_text_from_box(self, page: int, box: Tuple[int, int, int, int]) -> Optional[str]:
        """
        :param page:
        :param box:
        :return:
        """
        try:
            with pdfplumber.open(self.filename) as pdf:
                if page >= len(pdf.pages):
                    # log(f"Page {page + 1} out of range in {self.filename}")
                    return None
                cropped = pdf.pages[page].within_bbox(box)
                return cropped.extract_text().strip() if cropped else None
        except Exception as e:
            # log(f"pdfplumber error while reading box {box} on page {page}: {e}")
            return None

    def extract_fields_from_pdf(self, page_fields: dict, output_csv: str, debug_folder: str,
                                debug_mode: bool = False) -> List[List[str]]:
        all_rows = []
        try:
            with pdfplumber.open(self.filename) as pdf:
                for page_num, fields in page_fields.items():
                    if page_num >= len(pdf.pages):
                        log(f"Skipped {self.filename} (missing page {page_num + 1})")
                        row = [self.filename, f"Page {page_num + 1}"] + ['PAGE_MISSING'] * len(fields)
                        all_rows.append(row)
                        continue

                    page = pdf.pages[page_num]
                    row = [self.filename, f"Page {page_num + 1}"]
                    for field_name, box in fields.items():
                        text = self.read_text_from_box(page_num, box)
                        row.append(text or '-')
                    all_rows.append(row)

                    if debug_mode:
                        debug_img_path = os.path.join(debug_folder,
                                                      f"{os.path.splitext(os.path.basename(self.filename))[0]}_page{page_num + 1}_debug.png")
                        pdf.pages[page_num].to_image().save(debug_img_path)

        except Exception as e:
            log(f"Error processing {self.filename}: {e}")
            for page_num, fields in page_fields.items():
                row = [self.filename, f"Page {page_num + 1}"] + ['ERROR'] * len(fields)
                all_rows.append(row)

        return all_rows

    def generate_word_debugger(self, page_number: int, debug_folder: str):
        output_image = os.path.join(debug_folder, f"words_page{page_number + 1}_boxes.png")
        output_csv = os.path.join(debug_folder, f"words_page{page_number + 1}_coords.csv")

        try:
            with pdfplumber.open(self.filename) as pdf:
                if page_number >= len(pdf.pages):
                    log(f"Cannot debug. Page {page_number + 1} not found in {self.filename}")
                    return

                page = pdf.pages[page_number]
                words = page.extract_words()

                with open(output_csv, "w", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Word", "x0", "top", "x1", "bottom"])
                    for word in words:
                        writer.writerow([word['text'], word['x0'], word['top'], word['x1'], word['bottom']])

                im = page.to_image(resolution=150)
                draw = im.draw
                for word in words:
                    bbox = (word['x0'], word['top'], word['x1'], word['bottom'])
                    im.draw_rect(bbox, stroke="red", fill=None, stroke_width=1)
                    draw.text((word['x0'] + 2, word['top']), word['text'], fill="red")

                im.save(output_image)
                log(f"Debugger image and CSV saved to: {debug_folder}")

        except Exception as e:
            log(f"Error generating word debugger: {e}")

    def find_text_coordinates(self, search_text: str, page_number: int = 0, tolerance: int = 2) -> List[
        Tuple[int, int, int, int]]:
        search_text = search_text.strip().lower()
        boxes = []

        try:
            with pdfplumber.open(self.filename) as pdf:
                if page_number >= len(pdf.pages):
                    log(f"Page {page_number + 1} not found in {self.filename}")
                    return []

                page = pdf.pages[page_number]
                words = page.extract_words()
                if not words:
                    log(f"No words found on page {page_number + 1} of {self.filename}")
                    return []

                temp_phrase = ""
                temp_coords = []

                for word in words:
                    word_text = word['text'].strip().lower()

                    if word_text == search_text:
                        x0 = round(word['x0']) - tolerance
                        top = round(word['top']) - tolerance
                        x1 = round(word['x1']) + tolerance
                        bottom = round(word['bottom']) + tolerance
                        return [(x0, top, x1, bottom)]

                    if not temp_coords:
                        if search_text.startswith(word_text):
                            temp_phrase = word_text
                            temp_coords = [word]
                    else:
                        temp_phrase += " " + word_text
                        temp_coords.append(word)

                        if temp_phrase.strip() == search_text:
                            x0 = round(temp_coords[0]['x0']) - tolerance
                            top = round(min(w['top'] for w in temp_coords)) - tolerance
                            x1 = round(temp_coords[-1]['x1']) + tolerance
                            bottom = round(max(w['bottom'] for w in temp_coords)) + tolerance
                            return [(x0, top, x1, bottom)]

                        elif not search_text.startswith(temp_phrase.strip()):
                            temp_phrase = ""
                            temp_coords = []

                log(f"Phrase '{search_text}' not found on page {page_number + 1} of {self.filename}")
                return []

        except Exception as e:
            log(f"Error finding coordinates in {self.filename}: {e}")
            return []
