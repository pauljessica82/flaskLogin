from flask import Flask, request, render_template, redirect, url_for
from utils.sql_db import SqlDatabase
from utils.excel_db import ExcelDatabase as exceldb
import openpyxl as xl

app = Flask(__name__)

database = SqlDatabase('utils/login.db')


@app.route('/home')
@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        user = (first_name, last_name, email, phone, username, password)
        if not (first_name and last_name and email and phone and username and password):
            return render_template('create_user.html', info="You are missing one or more fields")
        else:
            database.insert_user(user)
            return redirect(url_for('dashboard', name=username))
    return render_template('create_user.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('user_dashboard.html')


@app.route('/create_post', methods=['POST', 'GET'])
def create_post():
    date = request.form.get('date')
    title = request.form.get('title')
    body = request.form.get('body')
    # user_id = (database.conn.cursor().execute('SELECT MAX(id) from users'))
    if not (title and body and date):
        return render_template('create_post.html', info='You are missing one or more fields')
    else:
        database.create_message(date, title, body)
        return redirect('/all_my_posts')


@app.route('/articles', methods=['POST', 'GET'])
def articles():
    query1 = database.conn.cursor().execute("""SELECT title, body from messages 
                                     WHERE messages.user_id in (SELECT users.id FROM users)""")
    messages = query1.fetchall()
    return render_template('all_posts.html', results=messages)


@app.route('/login', methods=['POST', 'GET'])
def valid_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = database.conn.cursor().execute('SELECT * FROM users where username = ? and password = ?',
                                              [username, password])
        if not (username and password):
            return render_template('login.html', info="you are missing one or more fields")
        elif not user.fetchone():
            return render_template('login.html', info='Invalid Credentials')
        else:
            return redirect(url_for('dashboard'))
    return render_template('login.html')


# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')
#
#     # is the page just opening
#     # yes
#     # > nothing
#     if not (username and password):
#         return render_template('login.html')
#     #
#     # no = logging in
#     # > successful or not
#     elif exceldb.invalid_credentials(username, password):
#         return render_template('login.html', info="Invalid Credentials")
#     else:
#         return render_template('create_post.html', name=username)


if __name__ == "__main__":
    app.run(debug=True)
