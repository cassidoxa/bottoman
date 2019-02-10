import sqlite3

class DatabaseManager:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()

    def query(self, arg, tup=()):
        self.c.execute(arg, tup)
        return self.c

    def write(self, arg, tup=()):
        self.c.execute(arg, tup)
        self.conn.commit()
        return self.c

    def close(self):
        self.conn.close()

    def __del__(self):
        self.conn.close()
