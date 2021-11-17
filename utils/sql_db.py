import sqlite3
from sqlite3 import Error


class SqlDatabase:
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
        except Error as e:
            print(e)

    def grab_all_posts(self):
        # messages = self.conn.cursor().execute('SELECT * FROM messages').fetchall()
        messages = self.conn.cursor().execute("""
        SELECT 
            users.first_name, users.last_name, messages.title, messages.body, messages.date
        FROM users INNER JOIN messages
        ON users.id  = messages.user_id; """).fetchall()
        return messages




    def create_table(self, create_table_sql):
        try:
            self.conn.cursor().execute(create_table_sql)
        except Error as e:
            print(e)

    def insert_user(self, user):
        self.conn.cursor().execute("""INSERT into users (first_name, last_name, phone, email, username, password) 
                                VALUES (?, ?, ?, ?, ?, ?)""", user)
        self.conn.commit()
        return self.conn.cursor().lastrowid

    def create_message(self, user_id, title, body, date):
        self.conn.cursor().execute("""INSERT INTO messages ( user_id, title, body, date) 
                                VALUES(?, ?, ?, ?)""", (user_id, title, body, date,))
        self.conn.commit()
        return self.conn.cursor().lastrowid


def main():
    sql_create_user_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        first_name text NOT NULL,
                                        last_name text NOT NULL,
                                        phone integer,
                                        email text NOT NULL,
                                        username text NOT NULL,
                                        password text NOT NULL
                                    ); """

    sql_create_messages_table = """CREATE TABLE IF NOT EXISTS messages (
                                    id integer PRIMARY KEY,
                                    user_id integer not NULL, 
                                    title text NOT NULL,
                                    body text NOT NULL, 
                                    date text NOT NULL,
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""
    database = SqlDatabase('login.db')
    database.create_table(sql_create_user_table)
    database.create_table(sql_create_messages_table)


if __name__ == '__main__':
    main()
