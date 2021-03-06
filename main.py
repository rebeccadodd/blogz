from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '7f5rgB!EOy_%HYRc'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if (request.endpoint not in allowed_routes
           and 'username' not in session
           and not request.path.startswith('/static/')):
        return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/newpost')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error_username = ""
        error_password = ""
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')

        elif user and user.password != password:
            error_password = "Password is invalid"
            return render_template('login.html', error_password=error_password)

        else:
            error_username = "Username does not exist"
            return render_template('login.html', error_username=error_username)
        
    return render_template("login.html", page_title='Login')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error_username = ""
        error_password = ""
        error_verify = ""

        if (username == ""
                or " " in username
                or len(username) < 3):
            error_username = "Please enter a valid username"

        if (password == ""
                or " " in password
                or len(password) < 3):
            error_password = "Please enter a valid password"

        if verify == "":
            error_verify = "Please enter a valid password"

        if verify != password:
            error_verify = "Passwords do not match"

        if (error_username == ""
            and error_password == ""
            and error_verify == ""):

            existing_user = User.query.filter_by(username=username).first()
            
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect("/newpost")
        
            else:
                error_username = "Username already exists"
                return render_template("signup.html", error_username=error_username)

        else:
            return render_template("signup.html", error_username=error_username,
                                                  error_password=error_password,
                                                  error_verify=error_verify,
                                                  username=username)
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route("/blog", methods=['GET'])
def blog():
    if "id" in request.args:
        blog_id = request.args.get("id")
        blog_entry = Blog.query.get(blog_id)
        return render_template("individualpost.html", blog_entry=blog_entry)

    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("individualuser.html", page_title = user.username + "'s Posts!", 
                                                      user_blogs=user_blogs)

    else:
        all_blogs = Blog.query.all()
        return render_template("blog.html", page_title="Blog posts!",
                                            all_blogs=all_blogs)

@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template("newpost.html", page_title="Add a New Blog Entry")

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error_title = ""
        error_body = ""

        if title == "":
            error_title = "Please fill in the title"

        if body == "":
            error_body = "Please fill in the body"

        if error_title == "" and error_body == "":
            new_blog_post = Blog(title, body, owner)
            db.session.add(new_blog_post)
            db.session.commit()
            new_blog_id = str(new_blog_post.id)
            return redirect("/blog?id=" + new_blog_id)

        else:
            return render_template("newpost.html", page_title="Add a Blog Entry",
                                                   error_title=error_title,
                                                   error_body=error_body,
                                                   title=title,
                                                   body=body)

@app.route("/", methods=['GET'])
def index():
    all_users = User.query.all()
    return render_template("index.html", page_title="Blog Users!",
                                         all_users=all_users)

if __name__ == '__main__':
    app.run()
    