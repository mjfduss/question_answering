import requests
from bs4 import BeautifulSoup

def main():

    ir_book_base_url = "https://nlp.stanford.edu/IR-book/html/htmledition/contents-1.html"

    page = requests.get(ir_book_base_url)

    soup_of_the_evening = BeautifulSoup(page.content, "html.parser")
    links = soup_of_the_evening.find_all('a')
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
    for link in content_links:
        print(link.get('href'), '|', link.text)

main() 