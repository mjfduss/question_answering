import uuid
import requests
from bs4 import BeautifulSoup

def find_child_pages(page):
    child_link_start = page.text.find("<!--Table of Child-Links-->")
    if child_link_start != -1:
        child_link_end = page.text.find("<!--End of Table of Child-Links-->")
        sub_page = page.text[child_link_start:child_link_end]
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

def process_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    return {
            'id': uuid.uuid4(),
            'link': url,
            'title': soup.title.string,
            'text': soup.get_text(),
            'children': find_child_pages(page)
        }


def crawl_textbook():

    ir_book_base_url = "https://nlp.stanford.edu/IR-book/html/htmledition/"

    page = requests.get(ir_book_base_url + 'contents-1.html')

    soup = BeautifulSoup(page.content, "html.parser")
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

    pages = list(
        map(
            process_page, 
            map(
                lambda link: ir_book_base_url + link.get('href'), 
                content_links)))
    
    return pages