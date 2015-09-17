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

# Two steps to preprocess the file:
# 1) Style information takes up the majority of the text in the file; it can be
#    removed using regular expressions before further processing takes place
# 2) <br> tags will be replaced with '\n' so that text may be more uniformly
#    extracted
with open('BMI-2013.12.31-10K.html') as f:
    html1 = re.sub(r' style=".*?"', '', f.read())
    html2 = re.sub(r'<br>', '\n', html1)
    soup = BeautifulSoup(html2)

body = soup.find('body')
# The plan for 'document.txt' is to iterate through the children tags in
# the body; getting the text content from them should be straightforward
with open('document.txt', 'w') as f1:
    for tag in body.children:
        text = str(tag) if isinstance(tag, NavigableString) else tag.get_text()
        if not text.endswith('\n'):
            text += '\n'
        f1.write(text)
# The tables don't look good, and some lines don't appear to have
# had line breaks appended to the end, but I'll look into
# 'paragraphs.txt' first
with open('document.txt') as f1:
    document_txt = f1.read()
paragraphs = []
search_chars = 20
for tag in body.children:
    # Exclude '$' found in tables
    if tag.find('table'):
        continue
    text = str(tag) if isinstance(tag, NavigableString) else tag.get_text()
    if '$' in text:
        start_index = document_txt.index(text[:search_chars])
        end_index = start_index + len(text)
        paragraphs.append({
            'text': text,
            'start': start_index,
            'end': end_index
        })
with open('paragraphs.txt', 'w') as f2:
    json.dump(paragraphs, f2)
# I wrote this script on a Windows machine, so the indexes seemed off.
# Once I set my text reader (Notepad++) to use '\n' instead '\r\n',
# the indexes were correct again.