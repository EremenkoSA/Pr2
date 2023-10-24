from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

app = Flask(__name__)
engine = sqlalchemy.create_engine("mariadb+mariadbconnector://root:1111@127.0.0.1:3306/pract")
app.config['SQLALCHEMY_DATABASE_URI'] = "mariadb+mariadbconnector://root:1111@127.0.0.1:3306/pract"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Event(db.Model):
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    date_start = db.Column(db.DATE, nullable=False)
    date_end = db.Column(db.DATE, nullable=False)
    link = db.Column(db.VARCHAR(100), nullable=False)
    def __repr__(self):
        return '<Event %r>' % self.id
 
class Qustions(db.Model):    
    q_id = db.Column(db.INT, primary_key=True)
    text = db.Column(db.VARCHAR(100), nullable=False)
    def __repr__(self):
        return '<Qustions %r>' % self.q_id

@app.route('/')
def index():
    event = Event.query.order_by(Event.date_start).all()
    return render_template("index.html", event=event)

@app.route('/report')
def report():
    return render_template("report.html")

@app.route('/create', methods=['POST', 'GET'])
def created_question():
    if request.method == "POST":
        text = request.form['text']

        questions = Qustions(text=text)
        try:
            db.session.add(questions)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("created_question.html")


@app.route('/survey', methods=['POST', 'GET'])
def survey():
    #return render_template("survey.html")
    if request.method == "POST":
        name = request.form['name']
        date_start = request.form['date_start']
        date_end = request.form['date_end']
        link = request.form['link']
        
        
        event = Event(name=name, date_start=date_start, date_end=date_end, link=link)
        try:
            db.session.add(event)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("survey.html")
    
if __name__ == "__main__":
    app.run(debug=True)