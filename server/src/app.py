import os
import pytz
import uuid

from datetime import datetime

from flask       import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_wtf   import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_mail  import Mail, Message

from itsdangerous      import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter

from forms       import LoginForm
from models      import User, Book, Comment

#-------------------------------------------------------------------
app = Flask(__name__)
app._static_folder = 'templates/static'

app.config['SECRET_KEY']          = '(Enter a personal salt key here)'
app.config['WTF_CSRF_ENABLED']    = True
app.config['WTF_CSRF_HEADERS']    = ['X-CSRFToken']
app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY'] 
app.config['MAIL_SERVER']         = 'smtp.gmail.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = '(your admin email account for sending welcome/reset emails)'
app.config['MAIL_PASSWORD']       = '(2FA app password for gmail or email password for others)'

login_manager            = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

csrf        = CSRFProtect(app)
cred        = credentials.Certificate('key.json')
default_app = initialize_app(cred)

db          = firestore.client()
s           = URLSafeTimedSerializer(app.config['SECRET_KEY'])

#-------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User(db.collection("users").document(user_id).get())


def get_user_by_email(email):
    users = db.collection("users").where(filter=FieldFilter("email", "==", email)).stream()
    for user in users:
        return User(user)
        
    return None

#-------------------------------------------------------------------
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.data['submit']:
        email    = form.email.data
        password = form.password.data
        remember = 'remember_me' in request.form
        user     = get_user_by_email(email)

        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name     = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        
        if get_user_by_email(email):
            flash("Email already exists. Login with your password or reset using Forgot Password.", 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user        = {'name'     : name, 
                           'password' : hashed_password, 
                           'email'    : email}
        db.collection('users').document(str(uuid.uuid4())).set(new_user)

        mail       = Mail(app)
        msg        = Message('Welcome to Not So Serious Bookworms', recipients=[email])
        msg.html   = f'''<img src="url_for('static', filename='banner.png')" style="max-width:500px;"/><br/><br/>
                        Hi {name},<br/>
                        <br />
                        Welcome to the world of Not So Serious Bookworms.<br/>
                        <br/>
                        Share books, reviews, laughs, love and friendships all in one place.<br/>
                        <br/>
                        Do let us know if you have feedback, ideas or trouble with the site (though I'm sure its all a-ok)<br/>
                        <br/>
                        Regards,<br/>
                        Administrator<br/>
                        (Not So Serious Bookworms)'''
        msg.sender = ('Not So Serious Bookworms', app.config['MAIL_USERNAME'])
        mail.send(msg)

        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user  = get_user_by_email(email)

        if user:
            mail       = Mail(app)
            token      = s.dumps(email, salt='password-reset-salt')
            reset_url  = url_for('reset_password', token=token, _external=True)
            msg        = Message('Password Reset (Not So Serious Bookworms)', recipients=[email])
            msg.html   = f'''
                            <img src="url_for('static', filename='banner.png')" style="max-width:500px;"/><br/><br/>
                            Hi {user.name},<br/>
                            <br />
                            We have received a password reset request for your account.<br/>
                            <br/>
                            Please use the following link to reset your password: <a href="{reset_url}">Reset Password</a><br/>
                            <br/>
                            This link will only be active for 1 hour. If expired, please use Reset Password again to trigger a fresh email.<br/>
                            <br/>
                            Please ignore if you have not initiated this request.<br/>
                            <br/>
                            Regards,<br/>
                            Administrator<br/>
                            (Not So Serious Bookworms)'''
            msg.sender = ('Not So Serious Bookworms', app.config['MAIL_USERNAME'])
            mail.send(msg)
        
        flash('If that is a valid account, you will receive an email with instructions.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The reset link is invalid or has expired. Please retry.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user         = get_user_by_email(email)

        if user:
            hashed_password = generate_password_hash(new_password)

            db.collection('users').document(user.id).update({'password' : hashed_password})
            mail       = Mail(app)
            msg        = Message('Password Reset (Not So Serious Bookworms)', recipients=[email])
            msg.html   = f'''<img src="url_for('static', filename='banner.png')" style="max-width:500px;"/><br/><br/>
                            Hi {user.name},<br/>
                            <br />
                            This is to inform you that your password has been reset.<br/>
                            <br/>
                            If you havent done this then please report to the admin now.<br/>
                            <br/>
                            Regards,<br/>
                            Administrator<br/>
                            (Not So Serious Bookworms)'''
            msg.sender = ('Not So Serious Bookworms', app.config['MAIL_USERNAME'])
            mail.send(msg)
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid User or Expired token. Please retry with valid details', 'danger')

    return render_template('reset_password.html', token=token)


#-------------------------------------------------------------------
@app.route('/add', methods=['POST', 'GET'])
@login_required
def add_book():
    if request.method == 'POST':
        title  = request.form['title']
        author = request.form['author']
        genre  = request.form['genre']
        rating = int(request.form['rating'])
        review = request.form['review']

        new_book = { 'title'        : title,
                     'title_search' : title.lower(),
                     'author'       : author, 
                     'genre'        : genre, 
                     'review'       : review, 
                     'rating'       : rating, 
                     'user_id'      : current_user.id,
                     'user'         : current_user.name,
                     'added'        : datetime.now(pytz.utc),
                     'likes'        : 0,
                     'comments'     : 0 }
        
        db.collection('books').document(str(uuid.uuid4())).set(new_book)

        flash('Book added successfully', 'success')
        return redirect(url_for('dashboard'))
    
    genre_coll = db.collection('genres').order_by('name', direction=firestore.Query.ASCENDING)
    genres     = [genre.get('name') for genre in genre_coll.stream()]
    return render_template('add_book.html', genres=genres)


@app.route('/book/<book_id>')
@login_required
def view_book(book_id):
    book      = Book(db.collection("books").document(book_id).get())
    comm_coll = db.collection("comments").where(filter=FieldFilter("book_id", "==", book_id ))\
                                         .order_by('added', direction=firestore.Query.ASCENDING)\
                                         .stream()
    comments  = [Comment(comment) for comment in comm_coll]
    likes     = db.collection("likes").where(filter=FieldFilter("book_id", "==", book_id ))\
                                      .where(filter=FieldFilter("user_id", "==", current_user.id)).stream()
    current_user_liked = len(list(likes)) > 0

    return render_template('view_book.html', book=book, comments=comments, current_user_liked=current_user_liked)


@app.route('/edit/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book(db.collection("books").document(book_id).get())
    if book.user_id != current_user.id and not current_user.is_admin():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        db.collection('books').document(book.id).update({ 
            'title'        : request.form['title'],
            'title_search' : request.form['title'].lower(),
            'author'       : request.form['author'], 
            'genre'        : request.form['genre'], 
            'review'       : request.form['review'], 
            'rating'       : int(request.form['rating']) })
        
        flash('Book details updated successfully.', 'success')
        return redirect(url_for('dashboard'))
    
    genre_coll = db.collection('genres').order_by('name', direction=firestore.Query.ASCENDING)
    genres     = [genre.get('name') for genre in genre_coll.stream()]

    return render_template('edit_book.html', book=book, genres=genres)


@app.route('/book/delete/<book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    comments = db.collection("comments").where(filter=FieldFilter("book_id", "==", book_id )).stream()
    for comment in comments:
        db.collection("comments").document(comment.id).delete()
    
    db.collection("books").document(book_id).delete()

    flash('Book deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/user/<user_id>/books', methods=['GET', 'POST'])
def user_books(user_id):
    page       = request.args.get('page', 1, type=int)
    per_page   = request.args.get('per_page', 10, type=int)
    sort_by    = request.args.get('sort_by', 'title')
    sort_order = request.args.get('sort_order', 'asc')

    user       = User(db.collection("users").document(user_id).get())
    book_query = db.collection("books").where(filter=FieldFilter("user_id", "==", user_id))
    
    if sort_order == 'desc':
        book_query = book_query.order_by(sort_by, direction=firestore.Query.DESCENDING)
    else:
        book_query = book_query.order_by(sort_by, direction=firestore.Query.ASCENDING)

    books_stream    = book_query.stream()
    books           = [Book(book) for book in books_stream]
    
    total_books     = len(books)
    start           = (page - 1) * per_page
    end             = start + per_page
    paginated_books = books[start:end]
    total_pages     = (total_books + per_page - 1) // per_page

    return render_template(
        'user_books.html',
        user        = user,
        books       = paginated_books,
        page        = page,
        per_page    = per_page,
        total_pages = total_pages,
        sort_by     = sort_by,
        sort_order  = sort_order
    )

#-------------------------------------------------------------------
@app.route('/book/<book_id>/add_comment', methods=['POST'])
@login_required
def add_comment(book_id):
    comment = request.form.get('comment')
    
    if comment:
        new_comment = { 
            'book_id'  : book_id, 
            'user_id'  : current_user.id,
            'user'     : current_user.name,
            'comment'  : comment,
            'added'    : datetime.now(pytz.utc) }
        
        db.collection('comments').document(str(uuid.uuid4())).set(new_comment)

        book     = db.collection('books').document(book_id).get()
        comments = book.to_dict()['comments']
        db.collection('books').document(book_id).update({'comments' : comments + 1})
    
    return redirect(url_for('view_book', book_id=book_id))


@app.route('/comment/delete/<comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment_obj = db.collection("comments").document(comment_id).get()
    comment     = Comment(comment_obj)

    if comment.user_id == current_user.id:
        db.collection("comments").document(comment_id).delete()

        book     = db.collection('books').document(comment.book_id).get()
        comments = book.to_dict()['comments']
        db.collection('books').document(comment.book_id).update({'comments' : comments - 1})

    return redirect(url_for('view_book', book_id=comment.book_id))


#-------------------------------------------------------------------
@app.route('/book/<book_id>/toggle_like', methods=['POST'])
@login_required
def toggle_like(book_id):
    book  = db.collection("books").document(book_id).get()
    likes = db.collection("likes").where(filter=FieldFilter("book_id", "==", book_id ))\
                                  .where(filter=FieldFilter("user_id", "==", current_user.id)).stream()
    likes = list(likes)
    total_likes = book.to_dict()['likes']

    if len(likes) > 0:
        for like in likes:
            db.collection("likes").document(like.id).delete()
            total_likes -= 1
    else:
        new_like = { 
            'book_id' : book_id, 
            'user_id' : current_user.id }
        db.collection('likes').document(str(uuid.uuid4())).set(new_like)
        total_likes += 1

    db.collection("books").document(book_id).update({'likes' : 0 if total_likes < 0 else total_likes})
    
    return jsonify({'status': 'success'})


#-------------------------------------------------------------------
@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    title_filter    = request.args.get('title', '').strip().lower()
    added_by_filter = request.args.get('added_by')
    genre_filter    = request.args.get('genre')
    
    page            = request.args.get('page', 1, type=int)
    per_page        = request.args.get('per_page', 10, type=int)
    sort_by         = request.args.get('sort_by', 'title')
    sort_order      = request.args.get('sort_order', 'asc')

    books_coll      = db.collection("books")

    if added_by_filter:
        books_coll = books_coll.where("user_id", "==", added_by_filter)
    if genre_filter:
        books_coll = books_coll.where("genre", "==", genre_filter)
    
    books_coll = books_coll.order_by(sort_by, 
                                     direction = firestore.Query.ASCENDING if sort_order == 'asc' \
                                            else firestore.Query.DESCENDING)
    
    all_books  = [book for book in books_coll.stream()]

    if title_filter:
        all_books = [book for book in all_books if title_filter in book.get('title').lower()]

    total_books = len(all_books)
    start       = (page - 1) * per_page
    end         = start + per_page
    books       = all_books[start:end]
    books       = [Book(book) for book in books]

    genres      = [book.genre for book in books]
    genres      = list(set(genres)) if genres else []
    
    user_list   = db.collection("users").stream()
    users       = [User(user) for user in user_list if user.id != '062cfa0e-aeb6-458a-9d11-97468c9f308d']

    total_pages = (total_books + per_page - 1) // per_page

    return render_template(
        'dashboard.html',
        books           = books,
        genres          = genres,
        users           = users,
        page            = page,
        total_pages     = total_pages,
        sort_by         = sort_by,
        sort_order      = sort_order,
        title_filter    = title_filter,
        added_by_filter = added_by_filter,
        genre_filter    = genre_filter
    )

#-------------------------------------------------------------------
@app.route('/manage_genres', methods=['GET', 'POST'])
@login_required
def manage_genres():
    if not current_user.is_admin():
        return redirect(url_for('dashboard'))

    genres_coll = db.collection("genres")

    if request.method == 'POST' and 'new_genre' in request.form:
        new_genre = request.form['new_genre'].strip()
        if new_genre:
            genres_coll.add({'name': new_genre})
            flash('Genre added successfully', 'success')
        else:
            flash('Invalid or Empty genre specified', 'danger')

    if request.method == 'POST' and 'rename_genre' in request.form:
        genre_id = request.form.get('genre_id')
        new_name = request.form.get('rename_genre').strip()

        if genre_id and new_name:
            genre_doc = genres_coll.document(genre_id).get()
            if genre_doc.exists:
                old_name = genre_doc.to_dict().get('name')

                genres_coll.document(genre_id).update({'name': new_name})

                books_coll = db.collection("books")
                books_to_update = books_coll.where('genre', '==', old_name).stream()

                for book in books_to_update:
                    book.reference.update({'genre': new_name})

            flash('Genre updated successfully', 'success')
        else:
            flash('Invalid or Empty genre specified', 'danger')

    if request.method == 'POST' and 'delete_genre' in request.form:
        genre_id = request.form['genre_id']
        genre_name = request.form['genre_name']

        books_with_genre = db.collection("books").where('genre', '==', genre_name).stream()
        if not any(books_with_genre):
            genres_coll.document(genre_id).delete()
            flash('Genre deleted successfully', 'success')
        else:
            flash('Genre cannot be deleted if tagged to books', 'danger')

    genres_coll = genres_coll.order_by('name', direction=firestore.Query.ASCENDING)
    genres = [genre.to_dict() | {'id': genre.id} for genre in genres_coll.stream()]

    return render_template('manage_genres.html', genres=genres)

#-------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))