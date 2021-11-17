from flask import Flask, request, render_template, redirect, url_for, session
from datetime import date as dt
from utils.sql_db import SqlDatabase
from utils.excel_db import ExcelDatabase as exceldb
import openpyxl as xl

app = Flask(__name__)
app.secret_key = "__privatekey__"
database = SqlDatabase('utils/login.db')


def allow(user_id):
    session['user_id'] = user_id


def logout():
    session.pop('user_id', None)


def check():
    return "user_id" in session


def user():
    return session.get('user_id')


@app.route('/logout')
def logged_out():
    logout()
    return render_template('logged_out.html')


@app.route('/home')
@app.route('/')
def hello():
    all_posts = database.grab_all_posts()
    return render_template('index.html', all_posts=all_posts)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirmed_password')
        user = (first_name, last_name, email, phone, username, password)
        # database.conn.cursor().execute('SELECT username FROM users')
        # existing_usernames = database.conn.cursor().fetchall()
        if not first_name and last_name and email and phone and username and password:
            return render_template('create_user.html', info="You are missing one or more fields")
        # # check if username is already taken
        # elif username in existing_usernames:
        #     return render_template('create_user.html', info="Username is already taken.")
        # elif password != confirmed_password:
        #     return render_template('create_user.html', info="Password and confirmed password do not match.")
        else:
            database.insert_user(user)
            return redirect(url_for('dashboard', name=username))
    return render_template('create_user.html')


def redirect_anon(func_view):
    def _replacemen_view():
        if not check():
            return redirect(url_for('valid_login'))

        return func_view()

    _replacemen_view.__name__ = func_view.__name__

    return _replacemen_view


# do not allow user to go to page without first signing in
@app.route('/dashboard', methods=['POST', 'GET'])
@redirect_anon
def dashboard():
    return render_template('user_dashboard.html')


@app.route('/create_post', methods=['POST', 'GET'])
@redirect_anon
def create_post():
    if request.method == 'POST':
        user_id = user()
        title = request.form.get('title')
        body = request.form.get('body')
        if not (title and body):
            return render_template('create_post.html', info='You are missing one or more fields')
        else:
            date = dt.today().strftime("%B %d, %Y")
            database.create_message(user_id, title, body, date)
            return redirect(url_for('articles'))
    return render_template('create_post.html')


@app.route('/articles', methods=['POST', 'GET'])
@redirect_anon
def articles():
    user_id = user()
    posts = database.conn.cursor().execute('SELECT title, body, date FROM messages WHERE user_id = ?',
                                           (user_id,)).fetchall()
    if not posts:
        return render_template('user_dashboard.html', info="No posts to show!! Please Create New Post")
    return render_template('my_posts.html', posts=posts)


@app.route('/login', methods=['POST', 'GET'])
def valid_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = database.conn.cursor().execute('SELECT id FROM users where username = ? and password = ?',
                                                 [username, password]).fetchone()
        # (id, user)
        if not (username and password):
            return render_template('login.html', info="You are missing one or more fields")
        elif not user_id:
            return render_template('login.html', info='Invalid Credentials')
        else:
            allow(user_id[0])
            return redirect(url_for('dashboard'))
    return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)
