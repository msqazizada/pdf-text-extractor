# PDF Data Extraction Tool

This tool extracts text from specific coordinates and pages in PDF files. It also includes OCR fallback when text extraction fails, making it suitable for scanned or image-based PDFs.

## ✅ Features
- Extract text from fixed coordinates (e.g., top-left, center)
- Support for multi-page PDFs
- Automatic OCR fallback (Tesseract)
- Output as CSV or JSON

---

## 🧱 Requirements

### macOS (using Homebrew)

```bash
brew install \
  python3 \
  imagemagick \
  tesseract \
  tesseract-lang \
  poppler \
  ghostscript \
  qpdf \
  unpaper
```
### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install -y \
  python3 \
  python3-pip \
  python3-dev \
  imagemagick \
  poppler-utils \
  tesseract-ocr \
  tesseract-ocr-eng \
  tesseract-ocr-deu \
  unpaper \
  ghostscript \
  qpdf \
  zlib1g \
  libmagic-dev
```
