"""Corrige ceps (postcode) do banco mongo para o formato canonico XX.XXX-XX
"""
from pymongo import MongoClient

def cepformat(cep):
    """Corrige o formato do cep

    Args:
        cep (string): cep a ser corrigido.

    Returns:
        param1 (string): cep reformatado, corrigido.
    """
    # reformata os ceps para o formato dos correios XX.XXX-XXX
    newcep = cep.replace('.', '').replace('-', '')
    return "{}.{}-{}".format(newcep[:2], newcep[2:5], newcep[5:])

def reformat():
    """Conecta ao mongo e reformata todos os ceps.
    """
    conn = MongoClient()
    database = conn.osm
    # percorre os documentos em busca dos que tenham codigo postal para
    # reformatar
    for elem in database.mapbsb.find({'address.postcode': {'$exists': True}}):
        newcep = cepformat(elem['address']['postcode'])
        database.mapbsb.update_one({'_id': elem['_id']},
                                   {'$set': {'address.postcode': newcep}})

if __name__ == "__main__":
    reformat()
