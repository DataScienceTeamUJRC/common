import requests
from bs4 import BeautifulSoup
import re
from neo4j.v1 import GraphDatabase,basic_auth

def generate_word_relation(sentence_word, word, relation):
    query_var = ""
    for k in sentence_word['properties'].keys():
        if query_var is not "":
            query_var += ', '
        query_var += "%s: \"%s\"" % (
            k,
            sentence_word['properties'][k]
        )
    query_var2 = ""
    for k in word['properties'].keys():
        if query_var2 is not "":
            query_var2 += ', '
        query_var2 += "%s: \"%s\"" % (
            k,
            word['properties'][k]
        )
    relation_properties = ""
    for k in relation['properties'].keys():
        if relation_properties is not "":
            relation_properties += ', '
        relation_properties += "%s: \"%s\"" % (
            k,
            relation['properties'][k]
        )

    query = 'MERGE (%s:%s {%s}) MERGE (%s:%s {%s}) MERGE (%s)-[%s:%s %s]->(%s) return %s;' % (
        sentence_word['node_prefix'],
        sentence_word['node_name'],
        query_var,
        word['node_prefix'],
        word['node_name'],
        query_var2,
        word['node_prefix'],
        relation['node_prefix'],
        relation['node_name'],
        "{%s}" % relation_properties if relation_properties != "" else "",
        sentence_word['node_prefix'],
        relation['node_prefix']
    )
    return query

def getLinks(articleUrl):
    html = requests.get(articleUrl)
    bsObj = BeautifulSoup(html.text, "html.parser")
    return bsObj


# Funcion encargada de recorrer el campo ("ul", {"class": "publ-list"}) para extraer todos los documentos asociado al
# autor en cuestión con sus coautores e incuir todas las relaciones al modelo de neo4j. como entrada hay que pasarle la
# estructura relativa al nodo del autor en cuestión y el objeto BS referente a la sección del html ("ul", {"class": "publ-list"})
# La funcion debuelve dos listas con los nombres y links de todos los coautores sin repetición.
def processBSauthor(author_neo1, years):
    n4j = GraphDatabase.driver('bolt://localhost:7687', auth=basic_auth('neo4j', 'sierna'))
    sesion = n4j.session()
    coauthors_names = []
    coauthors_links = []
    for year in years:
        for box in year:
            clas = dict(box.attrs).get('class', '')[0]
            if clas=="year":
                current_year= box.text
            elif clas == "entry":
                document_types= year.find("li", {"class": "data"})

                doc_title=box.find("span", {"class": "title"})
                clase = box.find("img")['title']
                author_names=box.find_all("span",{"itemprop":"name"})
                author_links=box.find_all("span", {"itemprop": "author"})
                file_link = box.find("li", {"class": "drop-down"}).find("a", href = True)
                if file_link == None:
                    file_link_url = "no file url"
                else:
                    file_link_url = file_link['href']
                #print(file_link)
                doc_neo  = {
                    "node_name": "document",
                    "node_prefix": "doc",
                    "properties": {
                        'name': doc_title.text,
                        'class': clase,
                        'year': current_year,
                        'file_link': file_link_url
                        }
                    }
                for pos, author in enumerate(author_links):
                    #print(author)
                    try:
                        author_link=author.find("a", href = True)
                        cbs = getLinks(author_link['href']) # Hace falta descargarse la pagina de cada coautor para poder obtener su url canónica.
                        current_link = cbs.find("head").find('link', {'rel': 'canonical'})['href']
                        author_neo2 = {
                        "node_name": "author",
                        "node_prefix": "author2",
                        "properties": {
                            'name': author.text,
                            'link': current_link
                            }
                        }
                        relation = {
                        "node_name": "relatedTo",
                        "node_prefix": "rlt",
                        "properties": {
                            "position": pos
                            }
                        }
                        #print(pos)
                        query = generate_word_relation(author_neo2, doc_neo, relation)
                        #print(query)
                        x = sesion.run(query)
                        if author.text not in coauthors_names:
                            coauthors_names.append(author.text)
                        #if author_link['href'] not in coauthors_links:
                            coauthors_links.append(current_link)


                    except Exception as e:
                        relation = {
                            "node_name": "relatedTo",
                            "node_prefix": "rlt",
                            "properties": {
                                "position": pos
                            }
                        }
                        query = generate_word_relation(author_neo1, doc_neo, relation)
                        #print(query)
                        x = sesion.run(query)
    return coauthors_names, coauthors_links

# Punto de partida Doctor Isaac Martin de Diego
authorLinkText = "Diego:Isaac_Mart=iacute=n_de"
bs = getLinks("http://dblp.uni-trier.de/pers/hd/d/" + authorLinkText)

#print(bs.find("span", {"class": "name primary"}).text)
author_seed_name = bs.find("span", {"class": "name primary"}).text
author_seed_link = bs.find("head").find('link', {'rel': 'canonical'})['href']
author_neo1 = {
    "node_name": "author",
    "node_prefix": "author1",
    "properties": {
        'name': author_seed_name,
        'link': author_seed_link
    }
}

years = bs.find_all("ul", {"class": "publ-list"})
names, links = processBSauthor(author_neo1, years)

coauthors_names = []
coauthors_links = []
for cont, name in enumerate(names):
    print(str(cont+1) + ' of ' + str(len(names)))
    bs =getLinks(links[cont])
    current_link = bs.find("head").find('link', {'rel': 'canonical'})['href']
    print(current_link)
    author_neo1 = {
        "node_name": "author",
        "node_prefix": "author1",
        "properties": {
            'name': bs.find("span", {"class": "name primary"}).text,
            'link': current_link
        }
    }
    years = bs.find_all("ul", {"class": "publ-list"})
    c_names, c_links = processBSauthor(author_neo1, years)
    for con2, name2 in enumerate(c_names):
        if (name2 not in names) & (name2 != author_seed_name):
            if name2 not in coauthors_names:
                coauthors_names.append(name2)
        #if c_links[con2] not in links:
            #if c_links[con2] not in coauthors_links:
                coauthors_links.append(c_links[con2])
print(names)
print(str(len(names)) + ' different authors added in the first level')
print(coauthors_names)
print(str(len(coauthors_names)) + ' different authors relationated in the second level')





