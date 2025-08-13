import time
import sqlite3 
import functools


query_cache = {}

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

def cache_query(func):
    """Decorator to cache the result of a query"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = kwargs.get('query')
        if query in query_cache:
            print("Using cached result")
            return query_cache[query]
        result = func(*args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")