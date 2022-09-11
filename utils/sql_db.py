import sqlite3
from sqlite3 import Error
import psycopg2
from psycopg2 import errors


class SqlDatabase:
    def __init__(self, db_file):
        # try:
            # self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn = psycopg2.connect(
            database=db_file
            )
        # except Error as e:
        #     print(e)

    def grab_blog_post_image(self, user_id):
        pic = self.conn.cursor().execute('SELECT photo from messages WHERE messages.user_id = ?',
                                         (user_id,)).fetchone()
        return pic

    def update_post(self, new_post):
        self.conn.cursor().execute('''
        UPDATE messages SET title = ? , body = ?  WHERE messages.id = ?
        ''', new_post)
        self.conn.commit()
        
    def delete_post(self, post_id):
        delete = self.conn.cursor().execute('DELETE FROM messages WHERE id = ? ', (post_id,))
        self.conn.commit()
        return delete

    def grab_user_id(self, username, password):
        user_id = self.conn.cursor().execute('SELECT id FROM users where username = ? and password = ?',
                                             [username, password]).fetchone()
        return user_id

    def grab_my_posts(self, user_id):
        posts = self.conn.cursor().execute('SELECT title, body, date, photo, id FROM messages WHERE user_id = ?',
                                           (user_id,)).fetchall()
        return posts

    def grab_all_posts(self):
        messages = self.conn.cursor().execute("""
        SELECT 
            users.first_name, users.last_name, messages.title, messages.body, messages.date, messages.photo
        FROM users INNER JOIN messages
        ON users.id  = messages.user_id; """).fetchall()
        return messages

    def create_table(self, create_table_sql):
        try:
            self.conn.cursor().execute(create_table_sql)
        except Exception as e:
            print(e)

    def insert_user(self, user):
        self.conn.cursor().execute("""INSERT into users (first_name, last_name, phone, email, username, password) 
                                VALUES (?, ?, ?, ?, ?, ?)""", user)
        self.conn.commit()
        return self.conn.cursor().lastrowid

    def create_message(self, user_id, title, body, date, photo):
        self.conn.cursor().execute("""INSERT INTO messages ( user_id, title, body, date, photo) 
                                VALUES(?, ?, ?, ?, ?)""", (user_id, title, body, date, photo))
        self.conn.commit()
        return self.conn.cursor().lastrowid
    
    def grab_user_info(self, user_id):
        user = self.conn.cursor().execute('SELECT first_name, last_name FROM users WHERE id = ?', (user_id,)).fetchall()
        return user
        


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
                                    photo blob NOT NULL, 
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""
    database = SqlDatabase('login.db')
    database.create_table(sql_create_user_table)
    database.create_table(sql_create_messages_table)


if __name__ == '__main__':
    main()
