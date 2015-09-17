"""
Parser for an SEC file format.

Outputs two documents: a 'document.txt' file
with the text information of the document
and a 'paragraphs.txt' file with the paragraphs
in the file that contain at least one '$' symbol.
"""

import json
import re
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from sys import argv


class SECParser(object):
    def __init__(self, file):
        self.text = file.read()
        self.soup = None
        self.search_chars = 20

    def preprocess(self):
        """
        Two steps to preprocess the file:
        1) Style information takes up the majority of the text in the file; it can be
           removed using regular expressions before further processing takes place
        2) <br> tags will be replaced with '\n' so that text may be more uniformly
           extracted
        """
        html1 = re.sub(r' style=".*?"', '', self.text)
        html2 = re.sub(r'<br>', '\n', html1)
        self.soup = BeautifulSoup(html2)

    def generate_document(self):
        """
        The plan for 'document.txt' is to iterate through the children tags in
        the body; getting the text content from them should be straightforward
        """
        body = self.soup.find('body')
        with open('document.txt', 'wb') as f1:
            for tag in body.children:
                text = (str(tag)
                        if isinstance(tag, NavigableString)
                        else tag.get_text())
                if not text.endswith('\n'):
                    text += '\n'
                f1.write(text.encode())

    def generate_paragraphs(self):
        """
        Because of nesting issues, this function recursively searches
        for paragraphs.
        :return:
        """
        def dig(hr_tag, end_index):
            paragraphs = []
            for tag in hr_tag.children:
                if tag.name == 'hr':
                    return paragraphs + dig(tag, end_index)
                text = (str(tag)
                        if isinstance(tag, NavigableString)
                        else tag.get_text())
                if '$' in text and not tag.find('table'):
                    start_index = document_txt.index(text[:search_chars])
                    end_index = start_index + len(text)
                    paragraphs.append({
                        'text': text,
                        'start': start_index,
                        'end': end_index
                    })
            return paragraphs

        with open('document.txt', 'rb') as f1:
            document_txt = f1.read().decode()
        search_chars = 20
        paragraphs = dig(self.soup.find('body'), 0)
        with open('paragraphs.txt', 'wb') as f2:
            f2.write(json.dumps(paragraphs).encode())


if __name__ == '__main__':
    try:
        filename = argv[1]
    except IndexError:
        print('Usage: python3 sec_parser.py <filename>')
        exit(1)

    with open(filename) as file:
        parser = SECParser(file)

    parser.preprocess()
    parser.generate_document()
    parser.generate_paragraphs()
