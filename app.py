from flask import Flask, request, render_template, redirect, url_for
from utils.sql_db import SqlDatabase
from utils.excel_db import ExcelDatabase as exceldb
import openpyxl as xl

app = Flask(__name__)
# adding secret key
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


# do not allow user to go to page without first signing in
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('user_dashboard.html')


@app.route('/create_post', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        body = request.form.get('body')
        date = request.form.get('date')
        if not (title and body and date):
            return render_template('create_post.html', info='You are missing one or more fields')
        else:
            database.create_message(title, body, date)
            return redirect(url_for('articles'))
    return render_template('create_post.html')


@app.route('/articles', methods=['POST', 'GET'])
def articles():
    posts = []
    # y u showing me everyone posts
    query1 = database.conn.cursor().execute("""SELECT title from messages 
                                     WHERE messages.user_id in (SELECT users.id FROM users)""")
    query2 = database.conn.cursor().execute("""SELECT body from messages 
                                        WHERE messages.user_id in (SELECT users.id FROM users)""")
    posts = query1.fetchall()
    content = query2.fetchall()
    return render_template('all_posts.html', posts=posts, content=content)


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
