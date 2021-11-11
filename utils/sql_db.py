import sqlite3
from sqlite3 import Error


class SqlDatabase:
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
        except Error as e:
            print(e)

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

    def return_user_id(self, user):
        user = self.retrieve_user()
        return self.conn.cursor().lastrowid

    def retrieve_user(self, username):
        self.conn.cursor().execute("""SELECT first_name, last_name, username, password FROM users 
                                    WHERE username=?", [username]""")
        user = self.conn.cursor().fetchone()
        # self.conn.close()
        return user

    def create_message(self, body, title, date):
        self.conn.cursor().execute("""INSERT INTO messages ( user_id, title, body, date) 
                                VALUES ((SELECT MAX(id) from users), ?, ?, ?)""", (title, body, date,))
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

