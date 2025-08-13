import sqlite3

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect('users.db')
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.connection.close()

with DatabaseConnection() as connection:
    cursor = connection.cursor()
    query = cursor.execute('''SELECT * FROM users''')
    print(query.fetchall())