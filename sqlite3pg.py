import sqlite3

conn = sqlite3.connect('instance/database.db')
cursor = conn.cursor()

cursor.execute("UPDATE user SET avg_rating = '0.00' WHERE avg_rating = '0';")
conn.commit()
conn.close()
