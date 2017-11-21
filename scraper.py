import requests
from bs4 import BeautifulSoup
import re


def getLinks(articleUrl):
    html = requests.get("http://dblp.uni-trier.de/pers/hd/d/" + articleUrl)
    bsObj = BeautifulSoup(html.text, "html.parser")
    return bsObj.findAll("li",{"class":"entry"}) #.findAll("a", href=re.compile("^(/wiki/)((?!:).)*$"))

links = getLinks("Diego:Isaac_Mart=iacute=n_de")
i=0
for link in links:
    #if "href" in link.attrs:
    print(link)
    i+=1
print(i)