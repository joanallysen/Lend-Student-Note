import sqlite3

conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS cart__item')
conn.commit()
conn.close()

