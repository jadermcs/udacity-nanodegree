#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Este modulo converte um arquivo xml do OpenStreetMap para o formato json e
em seguida o insere no banco MongoDB especificado na funcao `mongo_insert`.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pymongo import MongoClient

OSMF = 'map.osm'
OUTFILE = 'docs.json'

CREATED = ["version", "changeset", "timestamp", "user", "uid"]


def process_element(element):
    """Esta funcao converte uma tag xml do openstreetmap para um documento do
    mongodb.

    Args:
    element (:obj: ElementTree): tag a ser convertida.

    Returns:
        doc (dict): documento resultante.
    """
    doc = {}
    #: obtem os atributos da tag para converter cada tag em um atributo json
    elems = element.attrib
    doc['id'] = elems['id']
    doc['timestamp'] = elems['timestamp']
    doc['type'] = element.tag
    #: define o documento como visivel, caso a tag seja disponilizada de forma
    #: visivel
    if 'visible' in elems:
        doc['visible'] = elems['visible']
    else:
        doc['visible'] = 'false'
    #: caso seja uma tag geolocalizada cria o atributo LATitude para documento
    if 'lat' in elems:
        doc['pos'] = [float(elems['lat']), float(elems['lon'])]
    #: obtem dados de endereço da tag e constroi dicionario de atributos do
    #: endereco
    for _ in element.findall('tag'):
        doc['address'] = {}
        for elemtag in element.iter('tag'):
            if elemtag.attrib['k'].startswith("addr:"):
                doc['address'][elemtag.attrib['k'].lstrip("addr:")] =\
                                                    elemtag.attrib['v']
            else:
                doc[elemtag.attrib['k']] = elemtag.attrib['v']
        if doc['address'] == {}:
            del doc['address']
    #: obtem referencias da tag
    nref = element.find('nd')
    if nref:
        doc['node_refs'] = []
        for elemnd in element.iter('nd'):
            doc['node_refs'].append(elemnd.attrib['ref'])
    return doc

def process_data(osm_file, outf):
    """Processa todas as tags do arquivo osm para um documentos de um arquivo
    json.

    Args:
        osm_file (str): nome do arquivo xml(osm) que serao extraídas as tags.
        outf (str): nome do arquivo json que serao salvo os documentos
                    extraidos das tags.
    """
    with open(outf, 'w') as fop:
        tree = ET.parse(osm_file)
        root = tree.getroot()
        #: processa as tags desejadas utilizando da funcao `process_element`
        for tag in ['node', 'way', 'relation', 'area']:
            for elem in root.findall(tag):
                doc = process_element(elem)
                if doc:
                    fop.write(json.dumps(doc)+'\n')

def mongo_insert(filep):
    """Conecta ao database mongoDB em seguida acessa os documentos json e
    insere um por um no banco.

    Args:
        filep (str): nome do arquivo json para recuperar os documentos.
    """
    client = MongoClient('localhost', 27017)
    database = client.osm
    #: dropa colecao ja existente para nao reescrever dados
    database.mapbsb.drop()
    with open(filep, 'r') as fop:
        for line in fop.readlines():
            doc = json.loads(line)
            doc['timestamp'] = datetime.strptime(doc['timestamp'],
                                                 '%Y-%m-%dT%H:%M:%SZ')
            database.mapbsb.insert_one(doc)

if __name__ == "__main__":
    process_data(OSMF, OUTFILE)
    mongo_insert(OUTFILE)
