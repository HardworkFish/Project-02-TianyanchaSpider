import pymongo


class DBConnection:
    conn = None
    servers = "mongodb://localhost:27017"

    def connection(self):
        self.conn = pymongo.MongoClient(self.servers)

    def close(self):
        return self.conn.disconnet()

    def get_connection(self):
        return self.conn
