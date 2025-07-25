import inspect
from typing import Dict, List, Tuple

import pdfplumber

from src.data_extractor import DataExtractor
from src.match_strategy import RegexMatch


class CSVFields:
    """
    Extracts all field values from a PDF using registered get_ methods.
    """

    def __init__(self, filename: str):
        """
        :param filename:
        """
        self.filename = filename
        self.extractor = DataExtractor(filename)
        self._total_pages = None  # Lazy-loaded

    @property
    def total_pages(self) -> int:
        """Cache page count to avoid repeated PDF opening"""
        if self._total_pages is None:
            with pdfplumber.open(self.filename) as pdf:
                self._total_pages = len(pdf.pages)
        return self._total_pages

    def extract_all(self) -> Dict[str, str]:
        """
        Automatically calls all methods that start with 'get_' and merges their dict results.
        :return: dict: {"Field Name": "Extracted Value"}
        """
        results = {
            'File': self.filename,
            'Total Pages': self.total_pages,
        }

        # Get all get_* methods dynamically
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if name.startswith('get_') and name != 'get_':
                try:
                    results.update(method())
                except Exception as e:
                    results[name[4:]] = f"ERROR: {str(e)}"

        return results

    def _extract_field(
            self,
            label: str,
            page: int,
            positions: List[Tuple[int, int, int, int]],
            regex: str
    ) -> Dict[str, str]:
        """Unified extraction logic for all fields"""
        return {
            label: self.extractor.extract_text(
                page=page,
                boxes=positions,
                match_strategy=RegexMatch(regex)
            )
        }

    def get_hwt_number(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "HWT03-001663-A",
            "HWT03-002064-A",
            "HWT03-002183-C",
            "HWT03-005231-A"
        ]
        return self._extract_field(
            'HWT Nummer',
            0,
            [
                (90, 858, 552, 901),
                (90, 854, 552, 919),
                (87, 857, 550, 901),
                (90, 858, 552, 901),
                (136, 1287, 828, 1351)
            ],
            r"^HWT03-\d{6}-[A-Z]$"
        )

    def get_packungsart(self) -> dict:
        """
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "HL - OC",
            "HL - SOC",
            "HL - SQ"
        ]
        return self._extract_field(
            'Packungsart',
            0,
            [
                (925, 98, 1164, 148),
            ],
            r"^HL\s*-\s*[A-Z]{2,3}$"
        )

    def get_gitternetz(self) -> dict:
        """
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "03-0333",
            "03-1025",
            "03-0099",
            "03-1025"
        ]
        return self._extract_field(
            'Gitternetz',
            0,
            [
                (1207, 99, 1447, 148),
            ],
            r"^03-\d{4}$"
        )

    def get_gitternetz_version(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "AOJ--0333-H",
            "A03-1025-F",
            "A03-0099-H",
            "A03-1025-F"
        ]
        return self._extract_field(
            'Gitternetz Version',
            0,
            [
                (103, 252, 190, 263)
            ],
            r".(.)$"
        )

    def get_eutpd(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "EUTPD 11-1 PL - SET 2",
            "MOLDOVA - SET 1",
            "EUTPD 11-1 AT - SET 2",
            "CH -SET 2"
        ]
        return self._extract_field(
            'EUTPD',
            0,
            [
                (3581, 98, 3669, 148),
            ],
            r"(?i)EUTPD"
        )

    def get_landkurzel(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "EUTPD 11-1 PL - SET 2",
            "MOLDOVA - SET 1",
            "EUTPD 11-1 AT - SET 2",
            "CH -SET 2"
        ]
        return self._extract_field(
            'LanderKurzel',
            0,
            [
                (3581, 98, 3669, 148),
            ],
            r""
        )

    def get_land(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "EUTPD 11-1 PL - SET 2",
            "MOLDOVA - SET 1",
            "EUTPD 11-1 AT - SET 2",
            "CH -SET 2"
        ]
        return self._extract_field(
            'Land',
            0,
            [
                (3581, 98, 3669, 148),
            ],
            r""
        )

    def get_set(self) -> dict:
        """
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "SET 2",
            "EUTPD 11-1 PL - SET 2",
            "MOLDOVA - SET 1",
            "EUTPD 11-1 AT - SET 2",
            "CH -SET 2",
        ]
        return self._extract_field(
            'Set',
            0,
            [
                (3735, 98, 3915, 148)
            ],
            r"(?i)\bSET\s*\d+\b"
        )

    def get_freigabedatum(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "09.11.2020",
            "27.11.2017",
            "11.08.2017",
            "13.03.2017"
        ]
        return self._extract_field(
            'Freigabedatum',
            0,
            [
                (443, 3164, 634, 3192)
            ],
            r"^\d{2}\.\d{2}\.\d{4}$"
        )

    def get_software(self) -> dict:
        """
        @TODO
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)"
        ]
        return self._extract_field(
            'Software',
            0,
            [
                (438, 3222, 864, 3259)  # (14)
            ],
            r"^[A-Za-z\s]+(?=\s*\(\d+\))"
        )

    def get_software_version(self) -> dict:
        """
        :return: dictionary containing field name and field value
        """
        likely_results = [
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)",
            "Adobe Illustrator CC (14)"
        ]
        return self._extract_field(
            'Software Version',
            0,
            [
                (799, 3222, 864, 3259)  # (14)
            ],
            r"^\(\d{2}\)$"
        )

    def get_chw_calculation(self) -> dict:
        """
        If the PDF has 3 pages it is always the second page, else doesn't exist!

        :return: dictionary containing field name and field value
        """
        likely_results = [
            "CHW03-0099-H",
            "CHW03-0333-EU",
        ]
        return self._extract_field(
            'CHW Calculation',
            1 if self.total_pages == 3 else 0,
            [
                (176, 1285, 990, 1350)
            ],
            r"^CHW03-\d{4}-[A-Z]{1,2}$"
        )

    def get_hwc_calculation(self) -> dict:
        """
        It is always the last page whether 2 pages or 3 pages!

        :return: dictionary containing field name and field value
        """
        likely_results = [
            "HWC03-001662-A",
            "HWC03-001810-A",
            "HWC03-001940-A",
            "HWC03-002923-A"
        ]
        return self._extract_field(
            'HWC Calculation',
            self.total_pages - 1,
            [
                (130, 1285, 832, 1350)
            ],
            r"^HWC03-\d{6}-[A-Z]$"
        )
