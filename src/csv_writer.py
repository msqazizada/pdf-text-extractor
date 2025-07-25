import csv


class CSVWriter:
    def write(self, filepath: str, headers: list[str], data: list[str]) -> None:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerow(data)
