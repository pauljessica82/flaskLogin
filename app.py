import os

from flask import Flask, request, render_template, redirect, url_for, session, json

from datetime import date as dt

from utils.sql_db import SqlDatabase
# from utils.excel_db import ExcelDatabase as exceldb

# import openpyxl as xl

app = Flask(__name__)
app.secret_key = "__privatekey__"


database = SqlDatabase('utils/login.db')


# landing pages and functions
@app.route('/projects')
def projects():
    data = get_static_json("static/projects/projects.json")['projects']
    data.sort(key=order_projects_by_weight, reverse=True)

    tag = request.args.get('tags')
    if tag is not None:
        data = [project for project in data if tag.lower() in [project_tag.lower() for project_tag in project['tags']]]

    return render_template('projects.html', projects=data, tag=tag)


@app.route('/projects/<title>')
def project(title):
    projects = get_static_json("static/projects/projects.json")["projects"]
    in_project = next((p for p in projects if p['link'] == title), None)
    if in_project is not None:
        selected = in_project
    return render_template('project.html', project=selected)


def order_projects_by_weight(projects):
    try:
        return int(projects['weight'])
    except KeyError:
        return 0


def get_static_file(path):
    site_root = os.path.realpath(os.path.dirname(__file__))
    return os.path.join(site_root, path)


def get_static_json(path):
    return json.load(open(get_static_file(path)))


@app.route('/')
@app.route('/home')
def hello():
    return render_template('main_page.html')


# blog related
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
        if not first_name and last_name and email and phone and username and password:
            return render_template('create_user.html', info="You are missing one or more fields")
        else:
            database.insert_user(user)
            return redirect(url_for('dashboard', name=username))
    return render_template('create_user.html')


# redirect anonymous user
def redirect_anon(func_view):
    def _replacemen_view():
        if not check():
            return redirect(url_for('valid_login'))

        return func_view()

    _replacemen_view.__name__ = func_view.__name__

    return _replacemen_view


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
    posts = database.grab_my_posts(user_id)
    if not posts:
        return render_template('user_dashboard.html', info="No posts to show!! Please Create New Post")
    return render_template('my_posts.html', posts=posts)


@app.route('/update')
@redirect_anon
def edit_post():
    return render_template('update_post.html')


@app.route('/delete')
@redirect_anon
def delete_post():
    user_id = user()
    database.delete_post(user_id)
    return redirect(url_for('articles'))


@app.route('/blog')
def blog_posts():
    data = get_static_json("static/projects/projects.json")['projects']
    posts = database.grab_all_posts()
    return render_template('index.html', all_posts=posts, projects=data)


@app.route('/login', methods=['POST', 'GET'])
def valid_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = database.grab_user_id(username, password)
        print(user_id[0])
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
