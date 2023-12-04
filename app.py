from flask import Flask, render_template, url_for, request, redirect
import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import qrcode
from fpdf import FPDF

app = Flask(__name__)
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





#Создание ответа на определённый вопрос 
@app.route('/create_a', methods=['POST', 'GET'])
def created_answers():
    if request.method == "POST":
        event_id = request.form['event_id']
        questions_id = request.form['questions_id']
        grade = request.form['grade']
        comment = request.form['comment']

        answers = Answers(event_id=event_id, questions_id=questions_id, grade=grade, comment=comment)
        try:
            db.session.add(answers)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("created_answers.html")


#Cписок ответов
@app.route('/all_a')
def all_answer():
    all_answers = Answers.query.all()
    return render_template("all_answer.html", all_answers=all_answers)


#Подробности про ответ
@app.route('/a/<int:id>')
def a_view(id):
    view_a = Answers.query.get(id)
    return render_template("view_answer.html", view_a=view_a)

#Удаление ответа
@app.route('/a/<int:id>/del')
def a_delete(id):
    delete_a = Answers.query.get_or_404(id)

    try:
        db.session.delete(delete_a)
        db.session.commit()
        return redirect('/all_a')
    except:
        return "Приудалении произошла ошибка"


#Изменение ответа
@app.route('/a/<int:id>/update', methods=['POST', 'GET'])
def a_update(id):
    update = Answers.query.get(id)
    if request.method == "POST":
        update.event_id = request.form['event_id']
        update.questions_id = request.form['questions_id']
        update.grade = request.form['grade']
        update.comment = request.form['comment']

        try:
            db.session.commit()
            return redirect('/all_a')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("update_a.html", update=update)    




#ВОПРОСЫ
#ВОПРОСЫ
#ВОПРОСЫ
#Создание вопроса
@app.route('/create_q', methods=['POST', 'GET'])
def created_question():
    if request.method == "POST":
        text = request.form['text']

        questions = Questions(text=text)
        try:
            db.session.add(questions)
            db.session.commit()
            return redirect('/all_q')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("created_question.html")


#Cписок вопросов
@app.route('/all_q')
def all_question():
    all_questions = Questions.query.all()
    return render_template("all_question.html", all_questions=all_questions)


#Подробности про вопрос
@app.route('/q/<int:id>')
def q_view(id):
    view_q = Questions.query.get(id)
    return render_template("view_question.html", view_q=view_q)


#Удаление вопроса
@app.route('/q/<int:id>/del')
def q_delete(id):
    delete_q = Questions.query.get_or_404(id)

    try:
        db.session.delete(delete_q)
        db.session.commit()
        return redirect('/all_q')
    except:
        return "Приудалении произошла ошибка"


#Изменение вопроса
@app.route('/q/<int:id>/update', methods=['POST', 'GET'])
def q_update(id):
    update = Questions.query.get(id)
    if request.method == "POST":
        update.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/all_q')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("update_q.html", update=update)    











#ИВЕНТЫ
#ИВЕНТЫ
#ИВЕНТЫ
#Создание ивента заносим данные в бд и создаём qrcode сохраняем в отдельную папку
#Назнание пдфки с qrcode будет id ивента + .pdf 
#Будем просматривать прошедшие мероприятия и удалять qrcode 
@app.route('/create_e', methods=['POST', 'GET'])
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
        return render_template("created_event.html")


#Главная страница С кнопками Главная, Добавить опрос, Помощь, Выйти
#Добавить - опрос пока кидает на добавление вопроса
#Помощь - нужно написать инструкцию для изпользования сайти
#Выйти - будем логинится пока заглушка  
@app.route('/')
def index():
    #event = Event.query.filter(Event.date_start > current_date).all()
    event = Event.query.all()
    return render_template("index.html", event=event)


@app.route('/event/<int:id>')
def event_view(id):
    view = Event.query.get(id)
    return render_template("view.html", view=view)


#Удаление ивента
@app.route('/event/<int:id>/del')
def event_delete(id):
    delete_event = Event.query.get_or_404(id)

    try:
        db.session.delete(delete_event)
        db.session.commit()
        return redirect('/')
    except:
        return "Приудалении произошла ошибка"


#Изменение ивента
@app.route('/event/<int:id>/update', methods=['POST', 'GET'])
def event_update(id):
    update = Event.query.get(id)
    if request.method == "POST":
        update.name = request.form['name']
        update.date_start = request.form['date_start']
        update.date_end = request.form['date_end']
        update.link = request.form['link']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("update_event.html", update=update)    
    







#ФОРМА ид вопроса ид ивента
#Создание ответа на определённый вопрос 
@app.route('/create_f', methods=['POST', 'GET'])
def created_form():
    if request.method == "POST":
        event_id = request.form['event_id']
        questions_id = request.form['questions_id']

        form = Form(event_id=event_id, questions_id=questions_id)
        try:
            db.session.add(form)
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("created_form.html")


#Cписок ответов
@app.route('/all_f')
def all_form():
    all_form = Form.query.all()
    return render_template("all_form.html", all_form=all_form)


#Подробности про ответ
@app.route('/f/<int:id>')
def f_view(id):
    view_f = Form.query.get(id)
    return render_template("view_form.html", view_f=view_f)

#Удаление ответа
@app.route('/f/<int:id>/del')
def f_delete(id):
    delete_f = Form.query.get_or_404(id)

    try:
        db.session.delete(delete_f)
        db.session.commit()
        return redirect('/all_f')
    except:
        return "Приудалении произошла ошибка"


#Изменение ответа
@app.route('/f/<int:id>/update', methods=['POST', 'GET'])
def f_update(id):
    update = Form.query.get(id)
    if request.method == "POST":
        update.event_id = request.form['event_id']
        update.questions_id = request.form['questions_id']
        try:
            db.session.commit()
            return redirect('/all_f')
        except:
            return "Ошибка при довавлении"
    else:
        return render_template("update_f.html", update=update)   




if __name__ == "__main__":
    app.run(debug=True)    