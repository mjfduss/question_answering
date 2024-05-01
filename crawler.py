"""
Nathan Hartzler
CSC790-SP24-Project
"""
import os
import uuid
import requests
from bs4 import BeautifulSoup

OUT_FOLDER = "textbook/"

def download_single_page(base_url: str, html_file: str):
    """Downloads the given html_file from the given base_url
        and saves it to the OUT_FOLDER directory
    """
    page = requests.get(base_url + html_file)
    with open(OUT_FOLDER + html_file, 'wb') as file:
        file.write(page.content)

def get_page(base_url: str, html_file: str) -> str:
    """Checks if the html_file is in the OUT_FOLDER directory
        Downloads it if it isn't, then returns a string
        of the file's contents
    """
    if not os.path.isfile(OUT_FOLDER + html_file):
        download_single_page(base_url, html_file)

    with open(OUT_FOLDER + html_file, 'r') as file:
        return file.read()


def find_child_pages(page: str):
    """Parses through the html page and finds child links if they exist
        It has to parse through the unconventional <UL> list that doesn't
        have closing </LI> tags for its list items. Once parses, it returns
        a list of the page titles as strings
    """
    child_link_start = page.find("<!--Table of Child-Links-->")
    if child_link_start != -1:
        child_link_end = page.find("<!--End of Table of Child-Links-->")
        sub_page = page[child_link_start:child_link_end]
        sub_page = sub_page.strip()
        ul_start = sub_page.find("<UL>") + 4
        ul_end = sub_page.find("</UL>", len(sub_page) - 5)
        sub_page = sub_page[ul_start:ul_end]
        ul_count = 0
        for i in range(0, len(sub_page), 4):
            if sub_page[:i].find("<UL>") != -1:
                ul_count += 1
        sub_soup = BeautifulSoup(sub_page, "html.parser")
        for i in range(0,ul_count):
            if sub_soup.ul is not None:
                sub_soup.ul.decompose()
        children = list(
            map(
                lambda t: " ".join(t.split()),
                map(
                    lambda t: t.replace('\n', ''), 
                    filter(
                        lambda t: t != "References and further reading", 
                        map(
                            lambda link: link.get_text(), 
                            sub_soup.find_all('a'))))))

        return children
    else:
        return []

def process_page(arguments):
    """Given a base_url and html_name, this
        gets a string of the pages contents, 
        parses it using the Beautiful Soup library,
        then builds a dictionary object for each html page
    """
    base_url, html_name = arguments
    
    page = get_page(base_url, html_name)
    soup = BeautifulSoup(page, "html.parser")

    return {
            'id': str(uuid.uuid4()),
            'link': base_url + html_name,
            'title': soup.title.string,
            'text': soup.get_text(strip=True),
            'children': find_child_pages(page)
        }


def crawl_textbook():
    """If the html files from the ir_book_base_url have not been downloaded locally,
        then this downloads the table of contents page from the website and parses it,
        it then procedurally downloads each html page from the book and parses it
        into a list of dictionary objects. If there is already a local store, then the 
        local html files are used.
    """
    ir_book_base_url = "https://nlp.stanford.edu/IR-book/html/htmledition/"

    if not os.path.isdir(OUT_FOLDER):
        os.makedirs(OUT_FOLDER)

    contents_page = requests.get(ir_book_base_url + 'contents-1.html')

    soup = BeautifulSoup(contents_page.content, "html.parser")
    links = soup.find_all('a')
    content_links = []
    first_link_found = False
    for link in links:
        if not first_link_found:
            name = link.get('name')
            first_link_found = True if name == "tex2html524" else False
            if first_link_found:
                content_links.append(link)
        else:
            if link.get('href') == 'bibliography-1.html':
                break
            content_links.append(link)
    print("Crawling HTML Textbook Page Links")
    
    pages = list(
        map(
            process_page, 
            map(
                lambda link: (ir_book_base_url, link.get('href')), 
                content_links)))
    
    return pages