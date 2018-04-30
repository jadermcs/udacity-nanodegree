#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from pymongo import MongoClient
from datetime import datetime
import json

osmf = 'map.osm'
outfile = 'docs.json'

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

count = 0


def process_element(el):
    """
    Esta funcao converte uma tag xml do openstreetmap para um documento do
    mongodb, recebendo uma <tag> e retornando um {dicionario}.
    """
    doc = {}
    global count
    count += 1
    # obtem os atributos da tag para converter cada tag em um atributo json
    elems = el.attrib
    doc['id'] = elems['id']
    doc['timestamp'] = elems['timestamp']
    doc['type'] = el.tag
    # define o documento como visivel
    # caso a tag seja disponilizada de forma visivel
    if 'visible' in elems:
        doc['visible'] = elems['visible']
    else:
        doc['visible'] = 'false'
    # caso seja uma tag geolocalizada cria o atributo LATitude para o documento
    if 'lat' in elems:
        doc['pos'] = [float(elems['lat']), float(elems['lon'])]
    # obtem dados de endereço da tag e constroi dicionario de atributos do
    # endereco
    ttags = el.findall('tag')
    for ttag in ttags:
        doc['address'] = {}
        for x in el.iter('tag'):
            if x.attrib['k'].startswith("addr:"):
                doc['address'][x.attrib['k'].lstrip("addr:")] = x.attrib['v']
            else:
                doc[x.attrib['k']] = x.attrib['v']
        if doc['address'] == {}:
            del doc['address']
    # obtem referencias da tag
    nref = el.find('nd')
    if nref:
        doc['node_refs'] = []
        for x in el.iter('nd'):
            doc['node_refs'].append(x.attrib['ref'])
    return doc

def process_data(osm_file, outf):
    """
    Processa todas as tags do arquivo osm para um documentos de um arquivo json
    """
    data = []
    with open(outf, 'w') as fop:
        tree = ET.parse(osm_file)
        root = tree.getroot()
        # processa as tags desejadas utilizando da funcao process_element
        for tag in ['node', 'way', 'relation', 'area']:
            for el in root.findall(tag):
                doc = process_element(el)
                if doc:
                    data.append(doc)
                    fop.write(json.dumps(doc)+'\n')

    return data

def mongo_insert(filep):
    client = MongoClient('localhost', 27017)
    db = client.osm
    # dropa colecao ja existente para nao reescrever dados
    db.mapbsb.drop()
    with open(filep, 'r') as fop:
        for l in fop.readlines():
            doc = json.loads(l)
            doc['timestamp'] = datetime.strptime(doc['timestamp'],
                                                 '%Y-%m-%dT%H:%M:%SZ')
            db.mapbsb.insert_one(doc)

if __name__ == "__main__":
    process_data(osmf, outfile)
    mongo_insert(outfile)
