import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def create_user_activity_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER,
                duration INTEGER,
                date TEXT,
                joining_time TEXT,
                leaving_time TEXT,
                FOREIGN KEY(user_id) REFERENCES users(rowid)
            )
        """
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


db = Database("discord.db")
db.create_table()
db.close()
