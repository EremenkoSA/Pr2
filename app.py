from flask import Flask, render_template, url_for, request, redirect, flash
import datetime
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import qrcode
from fpdf import FPDF
from flask_login import LoginManager
from flask_login import login_user, login_required, logout_user
from flask_security import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

current_date = datetime.date.today()



login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


###КЛАССЫ
###КЛАССЫ
###КЛАССЫ
class User(db.Model, UserMixin):
    id = db.Column(db.INT, primary_key=True)
    login = db.Column(db.VARCHAR(100), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=False)
    is_active= db.Column(db.Boolean, default=True, nullable=False)
    def __init__(self, login, password):
        self.login = login
        self.password = password

    def is_authenticated(self):
        return True

    def is_user_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % self.id


class Event(db.Model):
    id = db.Column(db.INT, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    date_start = db.Column(db.DATE, nullable=False)
    date_end = db.Column(db.DATE, nullable=False)
    link = db.Column(db.VARCHAR(100), nullable=False)
    def __repr__(self):
        return '<Event %r>' % self.id
 
class Answers(db.Model):
    id = db.Column(db.INT, primary_key=True)
    event_id = db.Column(db.INT, db.ForeignKey('event.id'), nullable=False)
    questions_id = db.Column(db.VARCHAR(100), db.ForeignKey('questions.id'), nullable=False)
    grade = db.Column(db.INT, nullable=False)
    comment = db.Column(db.VARCHAR(100))
    def __repr__(self):
        return '<Answers %r>' % self.id
    
class Questions(db.Model):    
    id = db.Column(db.INT, primary_key=True)
    text = db.Column(db.VARCHAR(100), nullable=False)
    def __repr__(self):
        return '<Questions %r>' % self.id


class Form(db.Model):
    id = db.Column(db.INT, primary_key=True)
    event_id = db.Column(db.INT, db.ForeignKey('event.id'), nullable=False)
    questions_id = db.Column(db.VARCHAR(100), db.ForeignKey('questions.id'), nullable=False)
    def __repr__(self):
        return '<Form %r>' % self.id


#Авторизация просит пароль и логин, после успешной авторизации кинет на прошлую страницу 
@app.route('/login', methods=['POST', 'GET'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        #user.is_active = True

        if user and check_password_hash(user.password, password):
            login_user(user)

            next_page = request.args.get('next')
            print(next_page)
            if (next_page is None) or next_page == 'http://127.0.0.1:5000/logout':
                return redirect('/')
            else:
                return redirect(next_page)
        else:
            flash('Login or password not correct')   
    else:
        flash('Please fill login and password')  
    
    return render_template('login.html')


##Регистрация нужно ввести логин(уникальный) и дважды пароль
@app.route('/register', methods=['POST', 'GET'])
#@login_required
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Please, fill al fields')
        elif password != password2:
            flash('Passwords are not equel')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd) 
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))
    return render_template('register.html')


##Просто логаут
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect('login')


##Если пользователя кидает на страницу логин, вернёт неё его на прошлуе при авторизации
@app.after_request
def redirect_to_signin(responce):
    if responce.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return responce
    
##Вопросы по определённому ивенту
@app.route('/event_q/<int:id>') 
@login_required
def re1(id):
    results = db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).all()
    for form, questions in results:
        print(form.questions_id, questions.text) 
    return render_template("event_questions.html", res = results)    


#Отчёт с комментариями
@app.route('/event/report/<int:id>/admin')
@login_required
def admin_report(id):
    view = Event.query.get(id)
    qq= db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).order_by(Questions.id).all()
    results = db.session.query(Answers, Questions).join(Questions).filter(Answers.event_id == id).order_by(Questions.id).order_by(Answers.grade).all()
    qq1= db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).order_by(Questions.id).count()
    sum = 0
    arr = [0]*(10)
    arr2 = [0]*qq1
    i = 1
    for i in range(10):
        for answers, questions in results:
            if questions.id == i:  
                sum = sum + answers.grade
        rey = db.session.query(Answers, Questions).join(Questions).filter(Answers.event_id == id).filter(Questions.id == i).count()
        if rey != 0:
            arr[i-1] = round((sum/rey), 2)
        print(rey)
        sum = 0
        i = i + 1                      
    print(arr)
    for i in range(qq1):
        for j in range(10):
            if arr[j] != 0:
                arr2[i] = arr[j]
                del arr[j]
                break 
    print(arr2)               
    return render_template("report_admin.html", res = results, qq =qq, arr = arr2, view=view) 


#Отчёт без комментариев
@app.route('/event/report/<int:id>')
def re4(id):
    view = Event.query.get(id)
    view2 = Answers.query.filter_by(event_id = id).all()
    view3 = Questions.query.filter_by(id = Answers.questions_id).all()
    qq= db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).order_by(Questions.id).all()
    results = db.session.query(Answers, Questions).join(Questions).filter(Answers.event_id == id).order_by(Questions.id).order_by(Answers.grade).all()
    qq1= db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).order_by(Questions.id).count()
    sum = 0
    arr = [0]*(10)
    arr2 = [0]*qq1
    i = 1
    for i in range(10):
        for answers, questions in results:
            if questions.id == i:  
                sum = sum + answers.grade
        rey = db.session.query(Answers, Questions).join(Questions).filter(Answers.event_id == id).filter(Questions.id == i).count()
        if rey != 0:
            arr[i-1] =  round((sum/rey), 2)
        print(rey)
        sum = 0
        i = i + 1 
    for i in range(qq1):
        for j in range(10):
            if arr[j] != 0:
                arr2[i] = arr[j]
                del arr[j]
                break                           
    return render_template("report.html", qq =qq, arr = arr2, view=view, view2=view2, view3=view3)   


#Анкета по ивенту с id-ком
@app.route('/event/form/<int:id>',methods=['POST', 'GET'])
def re2(id):
    results = db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).all()
    for form, questions in results:
        print(form.id)
    ss = db.session.query(Form, Questions).join(Questions).filter(Form.event_id == id).count()
    print(ss)
    for form in range(1, ss):
        print()  

    if request.method == "POST":
        for form, questions in results:
            event_id = request.form['event_id'+str(form.id)]
            questions_id = request.form['questions_id'+str(form.id)]
            grade = request.form['grade'+str(form.id)]
            comment = request.form['comment-field'+str(form.id)]

            answers = Answers(event_id=event_id, questions_id=questions_id, grade=grade, comment=comment)
            db.session.add(answers)
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Ошибка при довавлении"
    else:         
        return render_template("form.html", res=results)


#Создание ответа на определённый вопрос, нужно было для теста можно убрать  
@app.route('/create_a', methods=['POST', 'GET'])
@login_required
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


#Cписок всех ответов нужно для теста можно убрать
@app.route('/all_a')
@login_required
def all_answer():
    #all_answers = Answers.query.all()
    all_answers = User.query.filter_by(login='raiden').first
    print(all_answers().is_active)
    print(all_answers().password)
    print(all_answers().login)
    print(all_answers().id)
    return render_template("all_answer.html", el=all_answers)


#Подробности про ответ по id 
@app.route('/a/<int:id>')
@login_required
def a_view(id):
    view_a = Answers.query.get(id)
    return render_template("view_answer.html", view_a=view_a)


#Удаление ответа по id
@app.route('/a/<int:id>/del')
@login_required
def a_delete(id):
    delete_a = Answers.query.get_or_404(id)

    try:
        db.session.delete(delete_a)
        db.session.commit()
        return redirect('/all_a')
    except:
        return "Приудалении произошла ошибка"


#Изменение ответа по шв
@app.route('/a/<int:id>/update', methods=['POST', 'GET'])
@login_required
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
@login_required
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


#Cписок всех вопросов
@app.route('/all_q')
@login_required
def all_question():
    all_questions = Questions.query.all()
    return render_template("all_question.html", all_questions=all_questions)


#Подробности про вопрос по id
@app.route('/q/<int:id>')
@login_required
def q_view(id):
    view_q = Questions.query.get(id)
    return render_template("view_question.html", view_q=view_q)


#Удаление вопроса по id
@app.route('/q/<int:id>/del')
@login_required
def q_delete(id):
    delete_q = Questions.query.get_or_404(id)

    try:
        db.session.delete(delete_q)
        db.session.commit()
        return redirect('/all_q')
    except:
        return "Приудалении произошла ошибка"


#Изменение вопроса по id
@app.route('/q/<int:id>/update', methods=['POST', 'GET'])
@login_required
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


#Справка для обычных пользователей, доступна по кнопке Помощь(редачить ссылку в template.html)
@app.route('/spravka')
def spravka():
    return render_template("spravka.html")

#Справка для админа доступна только по ссылке
@app.route('/spravka/admin')
@login_required
def spravka_admin():
    return render_template("spravkar.html")







#ИВЕНТЫ
#ИВЕНТЫ
#ИВЕНТЫ
#Создание ивента при создании вместа ссылки ставим заглушку 
@app.route('/create_e', methods=['POST', 'GET'])
@login_required
def survey():
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
#Добавить - кидает на добавление ивента
#Помощь - инструкцию для изпользования сайти
#Выйти - если не авторизирован кинет на логин, если авторизирован разлогинит и кинет на логин  
@app.route('/')
def index():
    ongoing_event = Event.query.filter(Event.date_start <= current_date, Event.date_end >= current_date).all()
    future_event = Event.query.filter(Event.date_start > current_date).all()
    past_event = Event.query.filter(Event.date_end < current_date).all()
    return render_template("index.html", ongoing_event=ongoing_event, future_event=future_event, past_event=past_event)


#Показывает Qr-code по ид ивента, генерирует его по ссылке ивента
@app.route('/event/qr/<int:id>')
def qr_view(id):
    view = Event.query.get(id)
    return render_template("qr.html", view=view)


#Показывает инфу по ивенту, кнопка добавление вопроса добавляет вопрос к общему пулу, а не в сам ивента 
@app.route('/event/<int:id>')
@login_required
def event_view(id):
    view = Event.query.get(id)
    return render_template("view.html", view=view)


#Удаление ивента, если в формах или ответа есть не даст удалить, доступно в '/event/<int:id>'
@app.route('/event/<int:id>/del')
@login_required
def event_delete(id):
    delete_event = Event.query.get_or_404(id)

    try:
        db.session.delete(delete_event)
        db.session.commit()
        return redirect('/')
    except:
        return "Приудалении произошла ошибка"


#Изменение ивента, доступно в '/event/<int:id>'
@app.route('/event/<int:id>/update', methods=['POST', 'GET'])
@login_required
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
@login_required
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


#Cписок всех форм(какой вопрос к какому ивенту)
@app.route('/all_f')
@login_required
def all_form():
    all_form = Form.query.all()
    return render_template("all_form.html", all_form=all_form)


#Подробности оперделённую форму нужно для тестов
@app.route('/f/<int:id>')
@login_required
def f_view(id):
    view_f = Form.query.get(id)
    return render_template("view_form.html", view_f=view_f)


#Удаление формы, если надо убрать возможность ответа на вопрос в необходимом ивенте 
@app.route('/f/<int:id>/del')
@login_required
def f_delete(id):
    delete_f = Form.query.get_or_404(id)

    try:
        db.session.delete(delete_f)
        db.session.commit()
        return redirect('/all_f')
    except:
        return "Приудалении произошла ошибка"


#Изменение формы
@app.route('/f/<int:id>/update', methods=['POST', 'GET'])
@login_required
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