import xmltodict
import json
import os
from html import unescape
from bs4 import BeautifulSoup
import lxml


# this function fetches the data from the xml file
def fetch(xml_file):
    with open(xml_file) as xmlFile:
        data = xmltodict.parse(xmlFile.read())
    if (isinstance(data['article']['submission_file'], list)):
        for i in range(len(data['article']['submission_file'])):
            if 'file' in data['article']['submission_file'][i]:
                del data['article']['submission_file'][i]['file']
    else:
        del data['article']['submission_file']['file']
    return data['article']


# this function selects the latest publication data
def selectLatest(data):
    if (isinstance(data['publication'], list)):
        return data['publication'][len(data['publication'])-1]
    else:
        return data['publication']


# To get all the authors from the article
def authorsList(data):
    lst = selectLatest(data)['authors']['author']
    out = []
    if (isinstance(lst, list)):
        for author in lst:
            out.append({
                "given_name": author['givenname']['#text'],
                "family_name": author['familyname']['#text'],
                "affiliation": author['affiliation']['#text'] if 'affiliation' in author else '',
                "country": author['country'],
                "email": author['email'],
                "bio": author['biography']['#text'] if 'biography' in author else ''
            })
    else:
        out.append({
            "given_name": lst['givenname']['#text'],
            "family_name": lst['familyname']['#text'],
            "affiliation": lst['affiliation']['#text'] if 'affiliation' in lst else '',
            "country": lst['country'] if 'country' in lst else '',
            "email": lst['email'] if 'email' in lst else '',
            "bio": lst['biography']['#text'] if 'biography' in lst else ''
        })
    return out


# to format the data into the required(json) format
def format(data):
    volume = selectLatest(data)['issue_identification']['volume'] if 'volume' in selectLatest(
        data)['issue_identification'] else ''
    number = selectLatest(data)['issue_identification']['number'] if 'number' in selectLatest(
        data)['issue_identification'] else ''
    first = str(data['id']['#text']) if 'id' in data else ''
    doid = f'10.3126/jiee.v{volume}i{number}.{first}'

    return {

        "url_id": str(data['id']['#text'] + '/' + selectLatest(data)['article_galley']['id']['#text']) if isinstance(selectLatest(data)['id'], list) else str(selectLatest(data)['id']['#text'] + '/' + selectLatest(data)['article_galley']['id']['#text']),
        "title": selectLatest(data)['title']['#text'],
        "doi_id": doid,
        "genre": data['submission_file'][0]['@genre'] if isinstance(data['submission_file'], list) else data['submission_file']['@genre'],
        "date_published": selectLatest(data)['@date_published'] if '@date_published' in selectLatest(data) else '',
        "abstract": selectLatest(data)['abstract']['#text'],
        "keywords": selectLatest(data)['keywords']['keyword'] if 'keywords' in selectLatest(data) else '',
        "discipline": selectLatest(data)['disciplines']['discipline'] if 'disciplines' in selectLatest(data) else '',
        "authors": authorsList(data),
        "submission_id": data['submission_file'][0]['@id'] if isinstance(data['submission_file'], list) else data['submission_file']['@id'],
        "volume": volume,
        "number": number,
        "year": selectLatest(data)['issue_identification']['year'] if 'year' in selectLatest(data)['issue_identification'] else '',
        "pages": selectLatest(data)['pages'] if 'pages' in selectLatest(data) else ''

    }
