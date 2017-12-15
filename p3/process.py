#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from pprint import pprint
from pymongo import MongoClient
import json

osmf = 'sample.osm'
outfile = 'docs.json'

CREATED = ["version", "changeset", "timestamp", "user", "uid"]

audit_file = 'audit.json'
faudit = open(audit_file, 'w')

count = 0


def proc_element(el):
    doc = {}
    global count
    count += 1

    elems = el.attrib
    doc['id'] = elems['id']
    doc['type'] = el.tag
    if 'visible' in elems:
        doc['visible'] = elems['visible']
    else:
        doc['visible'] = 'false'
    if 'lat' in elems:
        doc['pos'] = [float(elems['lat']), float(elems['lon'])]
    doc['created'] = {}
    for x in CREATED:
        doc['created'][x] = elems[x]
    ttag = el.find('tag')
    if ttag:
        doc['address'] = {}
        for x in el.iter('tag'):
            if x.attrib['k'].startswith("addr:"):
                doc['address'][x.attrib['k'].lstrip("addr:")] = x.attrib['v']
            else:
                doc[x.attrib['k']] = x.attrib['v']
        if doc['address'] == {}:
            del doc['address']
    nref = el.find('nd')
    if nref:
        doc['node_refs'] = []
        for x in el.iter('nd'):
            doc['node_refs'].append(x.attrib['ref'])
    if count % 20000 == 0:
        pprint(doc)
    return doc


def process_data(osm_file, outf):
    data = []
    with open(outf, 'w') as fop:
        tree = ET.parse(osm_file)
        root = tree.getroot()

        for el in root.findall('node'):
            doc = proc_element(el)
            if doc:
                data.append(doc)
                fop.write(json.dumps(doc)+'\n')

        for el in root.findall('way'):
            doc = proc_element(el)
            if doc:
                data.append(doc)
                fop.write(json.dumps(doc)+'\n')

        for el in root.findall('relation'):
            doc = proc_element(el)
            if doc:
                data.append(doc)
                fop.write(json.dumps(doc)+'\n')

        for el in root.findall('area'):
            doc = proc_element(el)
            if doc:
                data.append(doc)
                fop.write(json.dumps(doc)+'\n')

    return data


def mongo_insert(filep):
    client = MongoClient('localhost', 27017)
    db = client.osm
    with open(filep, 'r') as fop:
        for l in fop.readlines():
            db.mapbsb.insert_one(json.loads(l))


def main():
    process_data(osmf, outfile)
    mongo_insert(outfile)


if __name__ == "__main__":
    main()
