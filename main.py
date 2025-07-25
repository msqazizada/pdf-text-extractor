from src.csv_fields import CSVFields
from src.csv_writer import CSVWriter

results = "results.csv"
pdfs_dir = "./pdfs"


def run():
    filename = pdfs_dir + '/HWT03-001663-A-LowRes.pdf'
    fields = CSVFields(filename)
    extracted_data = fields.extract_all()
    writer = CSVWriter()
    headers = list(extracted_data.keys())
    data = list(extracted_data.values())
    writer.write('csv-file-path', headers, data)


if __name__ == '__main__':
    # run()
    filename = pdfs_dir + '/HWT03-001663-A-LowRes.pdf'
    fields = CSVFields(filename)
    print(fields.extract_all())
