import sqlite3

conn = sqlite3.connect('colleges-and-courses.db')
cursor = conn.cursor()

cursor.execute('''
            DROP TABLE IF EXISTS all_courses
               ''')
conn.commit()
conn.close()

print("Database successfully created")