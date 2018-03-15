import sys
import re
import os
import getopt
import PyPDF2
import chardet

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter,XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io

#converts pdf, returns its text content as a string
def convert_pdf2text(case,fname, pages=None):
    if not pages: pagenums = set();
    else:         pagenums = set(pages);      
    manager = PDFResourceManager() 
    codec = 'utf-8'
    caching = True

    if case == 'text' :
        output = io.StringIO()
        converter = TextConverter(manager, output, codec=codec, laparams=LAParams())     
    if case == 'HTML' :
        output = io.BytesIO()
        converter = HTMLConverter(manager, output, codec=codec, laparams=LAParams())

    interpreter = PDFPageInterpreter(manager, converter)   
    infile = open(fname, 'rb')

    for page in PDFPage.get_pages(infile, pagenums,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    convertedPDF = output.getvalue()  

    infile.close(); converter.close(); output.close()

    # --- Peculiarities of pdfminer ---
    # Convert ligatures back to original chars
    convertedPDF = re.sub(r'ﬂ', 'fl', convertedPDF)
    convertedPDF = re.sub(r'ﬁ', 'fi', convertedPDF)
    convertedPDF = re.sub(r'ﬀ', 'ff', convertedPDF)
    convertedPDF = re.sub(r'ﬃ', 'ffi', convertedPDF)
    convertedPDF = re.sub(r'ﬄ', 'ffl', convertedPDF)
    convertedPDF = re.sub(r'\(cid:\d+?\)', '', convertedPDF)

    return convertedPDF

def is_pdf(path_string):
    return (os.path.exists(path_string)
            and re.search(r"\.pdf$", path_string.lower()) != None)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:')
    except (getopt.GetoptError):
        print('hLDA_main.py -i <pdf-dir> -o <output-dir>')
        sys.exit(2)

    # Default directories
    input_dir = os.path.join('pdf-corpus', '')
    output_dir = os.path.join('extracted-text', '')

    for o, a in opts:
        if (o == '-i'):
            input_dir = a
            assert(os.path.isdir(input_dir) and os.path.exists(input_dir))
            print('PDF directory: ' + os.path.join(os.getcwd(), input_dir))  # TODO: Logging
        elif (o == '-o'):
            output_dir = a
            assert(os.path.isdir(output_dir) and os.path.exists(output_dir))
            print('Output directory: ' + os.path.join(os.getcwd(), output_dir))  # TODO: Logging
        else:
            print('Invalid option: ' + o)

    # Extract text from all PDFs
    for filename in os.listdir(input_dir):
        print('Converting PDF to text: ' + filename[:55] + '...')
        filepath = os.path.join(input_dir, filename)
        
        if not is_pdf(filepath):
            print('\t[Error] ' + filename + ' is not a PDF file.')
            continue
        try:
            extracted_text = convert_pdf2text('text', filepath)
        except Exception as err:
            print('\t[Error] Failed to convert PDF to text. ' + str(err))
            continue

        # Write to file
        text_file_obj = open(os.path.join(output_dir, os.path.splitext(filename)[0] + '.txt'), 'w', encoding='utf-8')
        text_file_obj.write(extracted_text)
        text_file_obj.close()

if (__name__ == '__main__'):
    main()
