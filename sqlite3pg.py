import sqlite3

conn = sqlite3.connect('sqlite:///database.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS note')
conn.commit()
conn.close()
