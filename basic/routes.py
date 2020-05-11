import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from basic import app, db, bcrypt
from basic.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, WordsForm
from basic.models import User, Post, Words
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/experience')
def experience():
    post_pm = Post.query.filter_by(category = 'Product Management').all()
    post_projects = Post.query.filter_by(category = 'Projects').all()
    return render_template('experience.html', post_pm=post_pm, title='experience', post_projects=post_projects)


@app.route('/inspiration')
def inspiration():
    post_goals = Post.query.filter_by(category = 'Goals').all()
    post_books = Post.query.filter_by(category = 'Books').all()
    return render_template('inspiration.html', post_goals=post_goals,  title='experience', post_books=post_books)

@app.route('/passions')
def passions():
    post_art = Post.query.filter_by(category = 'Art').all()
    post_music = Post.query.filter_by(category = 'Music').all()
    return render_template('Passions-page.html', title='Passions', post_art=post_art, post_music=post_music)

@app.route('/kindwords')
def kindwords():
    words = Words.query.all()   
    return render_template('kindwords.html', title='Kind Words', words=words)


@app.route("/sharewords", methods=['GET', 'POST'])
def sharewords():
    form = WordsForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            words.image_file = picture_file
        words = Words(name=form.name.data, content=form.content.data)
        db.session.add(words)
        db.session.commit()
        flash('Your words have been shared!', 'success')
        return redirect(url_for('index'))
    return render_template('sharewords.html', title='Share my experience',
                           form=form, legend='Words')

@app.route('/resume')
def resume():
    return render_template('resume.html', title='resume')

@app.route('/thankyou', methods= ['GET', 'POST'])
def thankyou():
    firstname = request.args.get('firstname')
    subject = request.args.get('subject')
    return render_template('thankyou.html', firstname=firstname, subject=subject, title='Thank you!')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route("/register", methods= ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data , password=hashed_password) #creating account
        db.session.add(user) #adding user to the database
        db.session.commit()
        flash('Your account has been created! You are now able to log in', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods= ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')#didn't fully understand this
            return redirect(next_page) if next_page else redirect(url_for('thankyou'))

      #hard-coded replaced by login manager:
      # if form.email.data == 'admin@blog.com' and form.password.data == 'password':
          #flash('You have been logged in!', 'success')
          #return redirect(url_for('thankyou')) #use sytnax of def
    #else:
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout(): #doesn't need any arguments because it knows which users are logged in
    logout_user()
    return redirect(url_for('index'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods= ['GET', 'POST']) #good for me when deleting posts
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user, category=form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))
    