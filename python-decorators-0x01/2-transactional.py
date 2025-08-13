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

def transactional(func):
    """Decorator to handle transactions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            args[0].commit()
            print("Transaction committed")
        except Exception as e:
            args[0].rollback()
            raise e
        return result
    return wrapper
    

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
#### Update user's email with automatic transaction handling

update_user_email(user_id=1, new_email="Crawford_Cartwright@hotmail.com")

#### Error handling test (THIS SHOULD RAISE AN EXCEPTION)

# update_user_email(user_id=1, new_email=None)


