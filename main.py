from datetime import date
import os
import werkzeug
from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, select, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, DataRequired, LoginForm, CommentForm
from typing import List
from dotenv import load_dotenv
import sys
print("Python version:", sys.version)
load_dotenv()
#test
'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author = relationship("User", back_populates="posts")
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    #relationships
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="post")


# Create a User table for all your registered users.
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    # relationships
    posts: Mapped[List["BlogPost"]] = relationship("BlogPost", back_populates="author")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="comment_author")

class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String(250), nullable=False)
    #Relationships
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="comments")




with app.app_context():
    db.create_all()


#Gravatar
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)



#decorator for admin only
def admin_only(func):
    @wraps(func)
    def wrapper():
        if current_user.is_authenticated:
            if current_user.id!=1:
                abort(403)
        else: abort(403)
        return func()
    return wrapper



# Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        test_user = User.query.filter_by(email=email).first()
        if test_user:
            flash('Email already registered, please log in!')
            return redirect(url_for('login'))
        name = form.name.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))

    return render_template("register.html", form=form)


# Retrieve a user from the database based on their email.
@app.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash('Incorrect password, please try again.')
                return redirect(url_for('login'))
        else:
            flash('This email hasn\'t been registered.')
            return redirect(url_for('login'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()

    for post in posts:
        print(post.author.name)

    return render_template("index.html", all_posts=posts, current_user=current_user)


# TAllow logged-in users to comment on posts
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must be logged in to post a comment!')
            return redirect(url_for('login'))
        else:
            text = form.body.data
            if text:
                db.session.add(Comment(text=text, comment_author=current_user, post=requested_post))
                db.session.commit()

    return render_template("post.html", post=requested_post, form=form)


# Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
