# Readme
## Скачать mariadb

## Установить зависимости из requirements.txt

Иногда не всё подтягивается, тогда прописываем сами эти команды
- pip install flask-security
- pip install flask-login
- pip install flask==2.3.3
- pip3 install pytz
- pip install -U Flask-SQLAlchemy
- pip3 install mariadb SQLAlchemy

### Кидаем файл 18.db в mariadb

Делаем соединение с бд, я делал через MySQL extensions для VSC  

### В config.py
Меняем ключ если надо
`app.config['SECRET_KEY'] = '<your_key>'`

### В config.py
```python 
app.config['SQLALCHEMY_DATABASE_URI'] = "maria+mariadbconnector://root:1111@127.0.0.1:3306/pract" 
```
**Из HeidiSQL**
- Вместо root имя пользователя
- Вместо 1111 пароль
- Вместо 3306 нужный порт
- Вместо 127.0.0.1 Имя хоста/IP
- Вместо практ имя бд

### В 103 строке
```python 
if (next_page is None) or next_page == 'http://127.0.0.1:5000/logout':
```    
Вместо `http://127.0.0.1:5000` пишем нужное

### Всё сохранить и можно запускать 


**Запуск с готовой БД аналогичен**  
Только файл 18.db не надо 


# !!
По умолчанию зарегистрировать админа с помощью `/register` может любой пользователь, следовательно и изменять бд 
Поэтому лучше после создание первого админа нужно раскомментировать строчку 111 `#@login_required`
Тогда новых админов сможет создавать только админ  
Важно чтобы связать вопрос с ивентом нужна запись в таблице form, без неё вопрос не появится в анкете  