from datetime import datetime
from databasemanager import DatabaseManager  
import pandas as pd
class Users(DatabaseManager):
    def __init__(self, db_name):
        super().__init__(db_name)
        self.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                Rate INTEGER)''', commit=True)
        self.execute('''
            CREATE TABLE IF NOT EXISTS rates (
                user_id INTEGER,
                date TIMESTAMP PRIMARY KEY,
                name_score INTEGER,
                organ_score INTEGER,
                feedback TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id))''', commit=True)

    def add_user(self, user_id, username, first_name, last_name):
        self.execute('''
            INSERT OR IGNORE INTO users (id, username, first_name, last_name)
            VALUES (?, ?, ?, ?)''', (user_id, username, first_name, last_name), commit=True)

    def get_users(self):
        return self.execute('SELECT * FROM rates', fetch=True)

    def search_user(self, user_name):
        users = self.execute('SELECT username FROM users', fetch=True)
        return any(user_name in user for user in users)

    def update_rate_and_feedback(self, user_id, name_score, organ_score, feedback):
        self.execute('''
            INSERT INTO rates (user_id, date, name_score ,organ_score, feedback)
            VALUES (?, ?, ?, ?, ?)''', (user_id, datetime.now(), name_score, organ_score, feedback), commit=True)

    def get_user_info(self, user_id):
        user_info = self.execute('''
            SELECT CONCAT(first_name || ' ' || last_name) FROM users
            WHERE id =?''', (user_id,), fetchone=True)
        return user_info[0]
    def clear_rate_table(self):
        self.execute('''DELETE FROM rates''', commit=True)
    def get_last_rate(self, user_id):
        try:
            last_rate = self.execute('''
                SELECT feedback FROM rates
                WHERE user_id =?
                ORDER BY date DESC
                LIMIT 1''', (user_id,), fetchone=True)
            return last_rate
        except:
            return None
    def get_scores_dataframe(self, user_id):
        try:
            scores = self.execute('''
                SELECT date,name_score, organ_score FROM rates
                WHERE user_id =?''', (user_id,), fetch=True)
            df = pd.DataFrame(scores, columns=['date','Correct name scores', 'Correct organ scores'])
            return df
        except:
            return None
user = Users('test.db')
print(user.get_users())
