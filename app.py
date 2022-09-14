import os


from flask import Flask, request, render_template, redirect, url_for, session, json, send_file

from werkzeug.utils import secure_filename

from datetime import date as dt

from utils.sql_db import SqlDatabase


app = Flask(__name__)
app.secret_key = "__privatekey__"
app.config["TEMPLATES_AUTO_RELOAD"] = True
# database = SqlDatabase('utils/login.db')
database = SqlDatabase()


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
        user = (first_name, last_name, phone, email, username, password)
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
    user_id = user()
    print(user_id)
    user_info = database.grab_user_info(user_id)
    print(user_info)
    name = user_info[0]
    return render_template('user_dashboard.html', name=name)


UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/post_detail')
def post_content():
    post_id = request.args.get('_id')
    title = request.args.get('title')
    first_name = request.args.get('authorfname')
    last_name = request.args.get('authorlname')
    author = [first_name, last_name]
    body_and_photo = database.grab_post_content(post_id)
    post = [title, author]
    return render_template('post_details.html', title=title, author=author, body=body_and_photo[0],
                           photo=body_and_photo[1])


@app.route('/create_post', methods=['POST', 'GET'])
@redirect_anon
def create_post():
    if request.method == 'POST':
        user_id = user()
        img = request.files['myFile']
        print(img.filename)
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            print(img.filename)
            print("Image Saved")

        title = request.form.get('title')
        body = request.form.get('body')
        photo = img.filename
        if not (title and body):
            return render_template('create_post.html', info='You are missing one or more fields')
        else:
            date = dt.today().strftime("%B %d, %Y")
            database.create_message(user_id, title, body, date, photo)
            return redirect(url_for('articles'))
    return render_template('create_post.html')


@app.route('/articles', methods=['POST', 'GET'])
@redirect_anon
def articles():
    user_id = user()
    print("user: " + str(user_id))
    user_info = database.grab_user_info(user_id)
    name = user_info[0]
    posts = database.grab_my_posts(user_id)
    if not posts:
        return render_template('user_dashboard.html', info="No posts to show!! Please Create New Post", name=name)
    return render_template('my_posts.html', posts=posts)


@app.route('/edit')
@redirect_anon
def edit_post():
    old_title = request.args.get('title')
    # old_post = request.args.get('post')
    post_id = request.args.get('_id')
    old_post = database.grab_post_content(post_id)[0]
    session['post_id'] = post_id
    print(old_title, old_post, post_id)

    return render_template('update_post.html', old_title=old_title, old_post=old_post)


@app.route('/update', methods=['POST', 'GET'])
@redirect_anon
def update_post():
    if request.method == 'POST':
        title = request.form.get('new_title')
        post = request.form.get('new_post')
        post_id = session.get('post_id')

        new_post = (title, post, post_id)
        print(new_post)

        if not (title and post):
            return render_template('update_post.html', info='You are missing one or more fields')
        else:
            database.update_post(new_post)
            print("Update successful")
            return redirect(url_for('articles'))

    return render_template('update_post.html')


@app.route('/delete', methods=['POST', 'GET'])
@redirect_anon
def delete_post():
    user_id = user()
    post_id = request.args.get('_id')
    user_posts = database.grab_my_posts(user_id)
    database.delete_post(post_id)

    print("deleted post")
    return redirect(url_for('articles'))


@app.route('/blog')
def blog_posts():
    posts = database.grab_all_posts()
    return render_template('index.html', all_posts=posts)


@app.route('/login', methods=['POST', 'GET'])
def valid_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = database.grab_user_id(username, password)
        if user_id:
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
