import sqlite3
from sqlite3 import Error
import psycopg2
from psycopg2 import errors
import os
from sqlalchemy import create_engine
import sqlalchemy as sa


class SqlDatabase:
    def __init__(self):
        try:
            engine = create_engine(os.getenv('SQLALCHEMY_DATABASE_URL'))
            self.conn = engine.connect()
        except Exception as e:
            print(e)

    def grab_blog_post_image(self, user_id):
        q = 'SELECT photo from messages WHERE messages.user_id = :user_id'
        pic = self.conn.execute(sa.text(q), {'user_id': (user_id,)}).fetchone()
        return pic

    def grab_post_content(self, post_id):
        q = 'SELECT body, photo from messages WHERE messages.id = :post_id'
        post = self.conn.execute(sa.text(q), {'post_id': (post_id,)}).fetchone()
        return post

    def update_post(self, new_post):
        q = 'UPDATE messages SET title = :title , body = :body  WHERE messages.id = :msg_id'
        self.conn.execute(sa.text(q), {'title': new_post[0], 'body': new_post[1], 'msg_id': new_post[2]})

    def delete_post(self, post_id):
        q = 'DELETE FROM messages WHERE id = :post_id'
        self.conn.execute(sa.text(q), {'post_id': post_id})

    def grab_user_id(self, username, password):
        q = 'SELECT id FROM users where username = :username and password = :password'
        user_id = self.conn.execute(sa.text(q), {'username': username, 'password': password}).fetchone()
        return user_id

    def grab_my_posts(self, user_id):
        q = 'SELECT title, body, date, photo, id FROM messages WHERE user_id = :user_id'
        posts = self.conn.execute(sa.text(q), {'user_id': (user_id,)}).fetchall()
        return posts

    def grab_all_posts(self):
        q = """
            SELECT 
                users.first_name, users.last_name, messages.title, messages.body, messages.date, messages.photo, 
            messages.id FROM users INNER JOIN messages
            ON users.id  = messages.user_id; """
        messages = self.conn.execute(sa.text(q)).fetchall()
        return messages

    def create_table(self, create_table_sql):
        try:
            self.conn.execute(create_table_sql)
        except Exception as e:
            print(e)

    def insert_user(self, user):
        q = """INSERT into users (first_name, last_name, phone, email, username, password) 
                                   VALUES :user """
        self.conn.execute(sa.text(q), {'user': user})

    def create_message(self, user_id, title, body, date, photo):
        q = """INSERT INTO messages ( user_id, title, body, date, photo) 
                                    VALUES(:user_id, :title, :body, :date, :photo)"""
        self.conn.execute(sa.text(q), {'user_id': user_id, 'title': title, 'body': body, 'date': date, 'photo': photo})

    def grab_user_info(self, user_id):
        q = 'SELECT first_name, last_name FROM users WHERE id = :id'
        user = self.conn.execute(sa.text(q), {'id': (user_id,)}).fetchall()
        return user


def main():
    sql_create_user_table = """ CREATE TABLE IF NOT EXISTS users (
                                        id serial PRIMARY KEY,
                                        first_name text NOT NULL,
                                        last_name text NOT NULL,
                                        phone text,
                                        email text NOT NULL,
                                        username text NOT NULL,
                                        password text NOT NULL
                                    ); """

    sql_create_messages_table = """CREATE TABLE IF NOT EXISTS messages (
                                    id serial PRIMARY KEY,
                                    user_id serial not NULL, 
                                    title text NOT NULL,
                                    body text NOT NULL, 
                                    date text NOT NULL,
                                    photo text NOT NULL, 
                                    FOREIGN KEY (user_id) REFERENCES users (id)
                                );"""
    # database = SqlDatabase('login.db')
    database = SqlDatabase()
    database.create_table(sql_create_user_table)
    database.create_table(sql_create_messages_table)


if __name__ == '__main__':
    main()
