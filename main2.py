from flask import Flask, request, render_template, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route("/blog", methods=['GET'])
def blog():
    all_blogs = Blog.query.all()
    return render_template("blog.html", page_title="Build a Blog",all_blogs=all_blogs)

@app.route("/newpost", methods=['GET', 'POST'])
def newpost():
    if request.method == 'GET':
        return render_template("newpost.html", page_title="Add a Blog Entry")

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
            new_blog_post = Blog(title, body)
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect("/blog")
        else:
            return render_template("newpost.html", page_title="Add a Blog Entry",
                                                   error_title=error_title,
                                                   error_body=error_body,
                                                   title=title,
                                                   body=body)

@app.route("/", methods=['GET'])
def index():
    return redirect("/blog")

if __name__ == '__main__':
    app.run()