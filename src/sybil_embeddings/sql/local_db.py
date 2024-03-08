import sqlite3

class BaseSQLModel:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def connect(self):
        pass

    def close(self):
        pass

    def execute(self, query: str):
        pass

    def fetchall(self):
        pass


def LocalSqlite(BaseSQLModel):
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def execute(self, query: str):
        self.cursor.execute(query)

    def fetchall(self):
        return self.cursor.fetchall()