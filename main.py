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

@app.route('/blog', methods=['GET'])
def index():
    if request.args:
        blog_id = request.args.get("id")
        blog = Blog.query.get(blog_id)
        return render_template('blogpost.html', blog=blog)

    else:
        all_blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", all_blogs=all_blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'GET':
        return render_template('newpost.html', title="Add Blog Entry") 

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog_post = Blog(blog_title, blog_body)
        db.session.add(new_blog_post)
        db.session.commit()
        blog_entry ="/blog?id=" + str(new_blog_post.id)
        return redirect(blog_entry)
    
    else:
        return render_template('newpost.html', title="Add Blog Entry")

if __name__ == '__main__':
    app.run()