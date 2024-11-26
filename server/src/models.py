from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, user_obj):
        user           = user_obj.to_dict()
        self.id        = user_obj.id
        self.name      = user['name']
        self.email     = user['email']
        self.password  = user['password']

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id
    
    def is_admin(self):
        # create an account on the website with the admin email address 
        # and fetch the guid from firestore db and paste here
        return self.id == 'guid of admin user in firestore db'
    

class Book:

    def __init__(self, book_obj):
        book          = book_obj.to_dict()
        self.id       = book_obj.id
        self.title    = book['title']
        self.author   = book['author']
        self.genre    = book['genre']
        self.review   = book['review']
        self.rating   = book['rating']
        self.user_id  = book['user_id']
        self.user     = book['user']
        self.added    = book['added']
        self.likes    = book['likes']
        self.comments = book['comments']


class Comment:

    def __init__(self, comment_obj):
        comment      = comment_obj.to_dict()
        self.id      = comment_obj.id
        self.book_id = comment['book_id']
        self.user_id = comment['user_id']
        self.user    = comment['user']
        self.comment = comment['comment']
        self.added   = comment['added']


class Like:

    def __init__(self, like_obj):
        like         = like_obj.to_dict()
        self.id      = like_obj.id
        self.book_id = like['book_id']
        self.user_id = like['user_id']