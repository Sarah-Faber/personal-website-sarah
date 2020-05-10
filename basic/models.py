from datetime import datetime
from basic import db, login_manager
from flask_login import UserMixin

#setting up extension which handles the sessions for us
#the extension expects the user model four attributes and or methods -  is authenticated, is active, is anonymous, GET id, add a class  UserMuixin which does it for you

@login_manager.user_loader #specify decorater 
def load_user(user_id):
    return User.query.get(int(user_id)) #get user by its id

class User(db.Model, UserMixin): #change the word user to commenter
    id = db.Column(db.Integer, primary_key=True) #unique ID for our user
    username = db.Column(db.String(20), unique=True, nullable=False) #make sure they are unique and have a username
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') #string to hash image_files
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True) #relationship not column, lazy prints out all the posts related to one user 
    
    #how our object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}'), '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


