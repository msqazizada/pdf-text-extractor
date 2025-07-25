import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Create shortcut function
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pdfextract").info
