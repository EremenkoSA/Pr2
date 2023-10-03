import mariadb
import sys

conn = mariadb.connect(
    user="root",
    password="1111",
    host="localhost",
    database="pract")
cur = conn.cursor() 