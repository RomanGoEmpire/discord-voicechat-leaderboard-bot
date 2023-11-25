import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS users")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL
            )
        """
        )
        self.conn.commit()

    def create_user_activity_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS user_activity")
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

    def user_exists(self, id):
        self.cursor.execute(
            """SELECT * FROM users WHERE id = ?""",
            (id,),
        )
        return self.cursor.fetchone() is not None

    def insert_user(self, id, username):
        self.cursor.execute(
            """
            INSERT INTO users (id, username) VALUES (?, ?)
        """,
            (id, username),
        )
        self.conn.commit()

    def insert_user_activity(self, user_id, duration, date, joining_time, leaving_time):
        self.cursor.execute(
            """
            INSERT INTO user_activity (user_id, duration, date, joining_time, leaving_time) VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, duration, date, joining_time, leaving_time),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    db = Database("discord.db")
    db.create_table()
    db.create_user_activity_table()
    db.close()
