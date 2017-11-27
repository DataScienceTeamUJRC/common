import requests
from bs4 import BeautifulSoup
import re

def getLinks(articleUrl):
    html = requests.get("http://dblp.uni-trier.de/pers/hd/d/" + articleUrl)
    bsObj = BeautifulSoup(html.text, "html.parser")

    return bsObj
    bsObj.find_all("li", {"class": "year"})

bs = getLinks("Diego:Isaac_Mart=iacute=n_de")

years=bs.find_all(("li", {"class": "year"}))

for year in years:
    document_types= year.find_all("li", {"class": "data"})
    boxes=year.find_all("div", {"class": "data"})
    for box in boxes:

        doc_title=box.find("span", {"class": "title"})
        author_names=box.find_all("span",{"itemprop":"name"})
        author_links=box.find_all("span", {"itemprop": "author"})
        for author in author_links:
          #  print(author)
            try:
                author_link=author.find("a").attrs['href']
                print(author_link)
            except:
                print("isaac")

        '''

        for author in author_names:
            print(author.text)
        print(doc_title.text)
'''





