from pymongo import MongoClient


def cepformat(cep):
    d = cep.replace('.', '').replace('-', '')
    return "{}.{}-{}".format(d[:2], d[2:5], d[5:])


def reformat():
    conn = MongoClient()
    db = conn.osm

    for x in db.mapbsb.find():
        if 'postcode' in x:
            newcep = cepformat(x['postcode'])
            db.mapbsb.update_one({'_id': x['_id']},
                                 {'$set': {'postcode': newcep}})


if __name__ == "__main__":
    reformat()
