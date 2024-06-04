import sqlite3

conn = sqlite3.connect('colleges-and-courses.db')
cursor = conn.cursor()

cursor.execute('''
            CREATE TABLE IF NOT EXISTS colleges (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               college_name TEXT NOT NULL
            )
        ''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               course_name TEXT NOT NULL,
               degree_type TEXT,
               college_id INTEGER
            )
        ''')

conn.commit()
conn.close()

print("Database successfully created")
