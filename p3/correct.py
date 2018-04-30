from pymongo import MongoClient


def cepformat(cep):
    # reformata os ceps para o formato dos correios XX.XXX-XXX
    d = cep.replace('.', '').replace('-', '')
    return "{}.{}-{}".format(d[:2], d[2:5], d[5:])

def reformat():
    conn = MongoClient()
    db = conn.osm
    # percorre os documentos em busca dos que tenham codigo postal para
    # reformatar
    for x in db.mapbsb.find({'address.postcode': {'$exists': True}}):
        newcep = cepformat(x['address']['postcode'])
        db.mapbsb.update_one({'_id': x['_id']},
                             {'$set': {'address.postcode': newcep}})

if __name__ == "__main__":
    reformat()
