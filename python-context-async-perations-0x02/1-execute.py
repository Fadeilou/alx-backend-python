import sqlite3

class ExecuteQuery:
    def __init__(self, age):
        self.age = age
        self.connection = None
    
    def __enter__(self):
        self.connection = sqlite3.connect('users.db')
        self.cursor = self.connection.cursor()
        return self.cursor.execute(f'''SELECT * FROM users WHERE age > {self.age}''')
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

with ExecuteQuery(25) as query:
    print(query.fetchall())