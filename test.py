from flask import Flask, render_template, url_for, request, redirect, flash
import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import qrcode
from fpdf import FPDF
from flask_login import LoginManager
from flask_login import login_user, login_required
from flask_security import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gfgfgghghgfhgfhgfhgfhfgghghghghghg'
app.config['SQLALCHEMY_DATABASE_URI'] = "mariadb+mariadbconnector://root:1111@127.0.0.1:3306/pract"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

current_date = datetime.date.today()





class Event(db.Model):
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    date_start = db.Column(db.DATE, nullable=False)
    date_end = db.Column(db.DATE, nullable=False)
    link = db.Column(db.VARCHAR(100), nullable=False)
    #ans = db.relationship('Answers', backref='author', lazy='dynamic')
    #answers = db.relationship("Answers", back_populates="event")
    def __repr__(self):
        return '<Event %r>' % self.id
 
class Answers(db.Model):
    id = db.Column(db.INT, primary_key=True)
    event_id = db.Column(db.INT, db.ForeignKey('event.id'), nullable=False)
    questions_id = db.Column(db.VARCHAR(100), db.ForeignKey('questions.id'), nullable=False)
    grade = db.Column(db.INT, nullable=False)
    comment = db.Column(db.VARCHAR(100))
    # event = db.relationship("Event", back_populates="answers")
    # questions = db.relationship("Questions", back_populates="answers")
    def __repr__(self):
        return '<Answers %r>' % self.id
    
class Questions(db.Model):    
    id = db.Column(db.INT, primary_key=True)
    text = db.Column(db.VARCHAR(100), nullable=False)
    #ans2 = db.relationship('Answers', backref='author', lazy='dynamic')
    #answers2 = db.relationship("Answers", back_populates="questions")
    def __repr__(self):
        return '<Questions %r>' % self.id


class Form(db.Model):
    id = db.Column(db.INT, primary_key=True)
    event_id = db.Column(db.INT, db.ForeignKey('event.id'), nullable=False)
    questions_id = db.Column(db.VARCHAR(100), db.ForeignKey('questions.id'), nullable=False)
    #grade = db.Column(db.INT, nullable=False)
    #comment = db.Column(db.VARCHAR(100))
    # event = db.relationship("Event", back_populates="answers")
    # questions = db.relationship("Questions", back_populates="answers")
    def __repr__(self):
        return '<Form %r>' % self.id
    

results = db.session.query(Form, Questions).join(Questions).all()

for form, questions in results:
    print(form.event_id, questions.text)    