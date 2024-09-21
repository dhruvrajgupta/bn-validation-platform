import PyPDF2

def pdf_to_text(pdf_path):

    # O<pen the PDF file in read-binary mode
    with open(pdf_path, 'rb') as pdf_file:
        # Create a PdfReader object instead of PdfFileReader
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Initialize an empty string to store the text
        text = ''

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()


    return text

print(pdf_to_text('/home/dhruv/Downloads/head-and-neck-tnm.pdf'))