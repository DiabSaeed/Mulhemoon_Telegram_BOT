import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=None, commit=False, fetch=False, fetchone=False):
        if params is None:
            params = ()
        self.cursor.execute(query, params)
        if commit:
            self.conn.commit()
        if fetch:
            return self.cursor.fetchall()
        if fetchone:
            return self.cursor.fetchone()

    def executemany(self, query, param_list, commit=False):
        self.cursor.executemany(query, param_list)
        if commit:
            self.conn.commit()

    def close(self):
        self.conn.close()

    def __del__(self):
        self.close()
