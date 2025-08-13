import sqlite3
import functools

def with_db_connection(func):
    """Decorator to open and close a database connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            connection = sqlite3.connect('users.db')
            result = func(connection, *args, **kwargs)
        finally:
            if connection:
                connection.close()
        return result
    return wrapper


@with_db_connection
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
#### Fetch user by ID with automatic connection handling 

user = get_user_by_id(user_id=1)
print(user)
