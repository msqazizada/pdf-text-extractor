from setuptools import setup, find_packages

# setup.py is used to define how your Python project is packaged and distributed.
# It allows you to install your code (and its dependencies) using `pip install .`
# and optionally expose command-line tools via entry points.

setup(
    name="pdf-text-extractor",  # Package name (used on PyPI if published)
    version="1.0.0",            # Version of your tool
    author="Salim Qazizada",    # Author name
    description="Extracts fixed-position fields from PDFs using OCR fallback.",

    # Automatically find all Python modules inside the 'src/' directory
    packages=find_packages(where="src"),
    package_dir={"": "src"},  # Treat 'src/' as the package root

    include_package_data=True,  # Include any non-code files specified in MANIFEST.in

    # External dependencies that will be installed automatically with the package
    install_requires=[
        "pytesseract",
        "pdf2image",
        "pdfplumber",
        "Pillow",
        "ocrmypdf",
        "tqdm",  # Optional: used for progress bar in batch processing
    ],

    # Define a command-line script called `pdfextract` that runs extract.py's main()
    entry_points={
        "console_scripts": [
            "pdfextract=extract:main",  # command=module:function
        ]
    },

    # Minimum Python version required
    python_requires=">=3.7",
)
