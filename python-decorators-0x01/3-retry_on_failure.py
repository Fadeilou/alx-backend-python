import time
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

def retry_on_failure(retries=3, delay=2):
    """Decorator to retry a function call in case of failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    print(f"Error: {e}\nRetrying in {delay} seconds...\n")
                    time.sleep(delay)
                else:
                    return result
            return "Error executing function (Max retries exceeded)"
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)

"""
# Error handling test (THIS SHOULD RAISE AN EXCEPTION)
@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry_fail(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT non_existent FROM users")
    return cursor.fetchall()

# Error handling test (THIS SHOULD RAISE AN EXCEPTION)

users = fetch_users_with_retry_fail()
print(users)
"""