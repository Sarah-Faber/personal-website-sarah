from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '06f8d0cb1db6e60f616c3354f7ea85a7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #creation of database
db = SQLAlchemy(app) #creating database instance 
bcrypt = Bcrypt(app)
login_manager = LoginManager(app) #will handle all the sessions for us
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' #info - class from bootstrap

from basic import routes