import sqlite3

db = sqlite3.connect('PraktModel.sql')

c = db.cursor()

#c.execute(""" CREATE TABLE Event (
#          event_id INTEGER,
#          name TEXT,
#          date_start TEXT,
#          date_end TEXT,
#          link TEXT
#)""")

#c.execute("INSERT INTO Event VALUES ('1', 'dfsd', date('now', +'1 hour'), date('now', +'5 days'), 'bubna.com')")
#c.execute("DELETE FROM Event WHERE rowid = '1'")
c.execute("SELECT  * FROM Event")
print(c.fetchall())
#print(c.fetchmany(1))
db.commit()
db.close()