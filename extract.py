#!/usr/bin/env python3
import argparse
import csv
import os
import subprocess
import time

from src.csv_fields import CSVFields


def preprocess_pdf(input_path: str) -> str:
    """
    Runs ocrmypdf to clean and deskew the input PDF.
    Returns path to preprocessed output.
    """
    output_path = input_path.replace(".pdf", "_cleaned.pdf")
    try:
        subprocess.run([
            "ocrmypdf",
            "--deskew",
            "--clean",
            "--optimize", "3",
            input_path,
            output_path
        ], check=True)
        return output_path
    except subprocess.CalledProcessError:
        print(f"[ERROR] Failed to preprocess {input_path}")
        return input_path  # Fallback to original


def process_pdf(pdf_path: str, preprocess: bool = False) -> dict:
    """
    Extract all fields from one PDF and return the result dict.
    """
    path = preprocess_pdf(pdf_path) if preprocess else pdf_path
    start = time.perf_counter()
    fields = CSVFields(path)
    result = fields.extract_all()
    result["Time (s)"] = round(time.perf_counter() - start, 2)
    return result


def write_results_to_csv(results: list, output_file: str):
    if not results:
        print("[INFO] No results to write.")
        return

    keys = results[0].keys()
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

    print(f"[✔] Results saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Extract fixed-field text from PDFs using OCR fallback.")
    parser.add_argument("input", help="PDF file or directory to process")
    parser.add_argument("-o", "--output", help="CSV output file", default="output.csv")
    parser.add_argument("--preprocess", action="store_true", help="Preprocess PDFs with ocrmypdf")
    args = parser.parse_args()

    files = []
    if os.path.isdir(args.input):
        files = [os.path.join(args.input, f) for f in os.listdir(args.input) if f.lower().endswith(".pdf")]
    elif os.path.isfile(args.input):
        files = [args.input]
    else:
        print("[ERROR] Invalid input path.")
        return

    results = []
    for pdf_file in files:
        print(f"[→] Processing {pdf_file}...")
        result = process_pdf(pdf_file, preprocess=args.preprocess)
        results.append(result)

    write_results_to_csv(results, args.output)


if __name__ == "__main__":
    main()
