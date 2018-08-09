import op_db
dbConn = op_db.DBConnection()
conn = None


def process():
    dbConn.connection()
    global conn
    conn = dbConn.get_connection()

    print(conn.server_info())
    databases = conn.database_names()
    print(databases)

    db = conn.db_tyc_merge
    # 连接数据库 db_tyc_collection_result
    collection = db['db_tyc_collection_result']
    # 连接数据库 db_tyc_certificate
    collection_certificate = db['db_tyc_certificate']
    print(collection.find().count())
    print(collection_certificate.find().count())
    cursor = collection.find({}, {"company_certificate": 1, "url": 1, "_id": 1})
    # 搜索并返回指定字段
    for document in cursor:
        # noinspection PyBroadException
        try:
            lists = document['company_certificate']
            if len(lists) > 0:
                print(lists)
                for key, value in lists.items():
                    if '国家测绘资质' in value:
                        _id = document['_id']
                        print(id, key, ':', value)
                        move_document = collection.find_one({"_id": _id})
                        # print(move_document)
                        collection_certificate.insert(move_document)
                        collection.remove({"_id": _id})

        except BaseException:
            continue
if __name__ == '__main__':
    process()
