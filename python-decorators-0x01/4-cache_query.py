import time # Not strictly needed here but often used with caching (e.g., TTL)
import sqlite3 
import functools
import os

# --- Database Setup ---
def setup_database():
    db_file = 'users.db'
    if os.path.exists(db_file):
        os.remove(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    sample_users = [ (1, 'Alice Smith', 'alice.smith@example.com'), (2, 'Bob Johnson', 'bob.johnson@example.com') ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", sample_users)
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' set up for 4-cache_query.py.")
# --- End Database Setup ---

# Global cache dictionary
query_cache = {}

# Copied from Task 1
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            print(f"Database error in with_db_connection: {e}")
            raise
        finally:
            if conn:
                conn.close()
    return wrapper

def cache_query(func):
    """
    Decorator that caches query results based on the SQL query string.
    Assumes the query string is passed as a keyword argument 'query'
    or as the first positional argument after 'conn'.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs): # conn is from with_db_connection
        query_string = None
        # Extract query string: from kwargs['query'] or args[0]
        if 'query' in kwargs:
            query_string = kwargs['query']
        elif args: # query is the first arg after conn
            query_string = args[0]
        
        if not query_string or not isinstance(query_string, str):
            # If query string cannot be identified, bypass cache
            print("CACHE: Could not identify query string, bypassing cache.")
            return func(conn, *args, **kwargs)

        # For more complex scenarios, consider arguments to the query as part of the cache key
        # For this task, just the query string is enough.
        cache_key = query_string 

        if cache_key in query_cache:
            print(f"CACHE: Returning cached result for query: {query_string}")
            return query_cache[cache_key]
        else:
            print(f"CACHE: No cache hit for query: {query_string}. Executing function.")
            result = func(conn, *args, **kwargs) # Pass query string via args/kwargs
            query_cache[cache_key] = result
            return result
    return wrapper


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query): # The query string is passed here
    print(f"DB: Executing query: {query}")
    # time.sleep(1) # Simulate a slow query
    cursor = conn.cursor()
    cursor.execute(query) # Query string used here
    return cursor.fetchall()

if __name__ == "__main__":
    setup_database()
    print("\nFetching users with caching:")

    print("--- First call (should execute and cache) ---")
    users = fetch_users_with_cache(query="SELECT * FROM users")
    # print("Users (1st call):", users)

    print("\n--- Second call (should use cached result) ---")
    users_again = fetch_users_with_cache(query="SELECT * FROM users")
    # print("Users (2nd call, cached):", users_again)

    print("\n--- Third call with different query (should execute and cache) ---")
    alice = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice Smith'")
    # print("Alice (3rd call):", alice)
    
    print("\n--- Fourth call, same as third (should use cached result) ---")
    alice_again = fetch_users_with_cache(query="SELECT * FROM users WHERE name = 'Alice Smith'")
    # print("Alice (4th call, cached):", alice_again)

    print("\nFinal cache state:", query_cache.keys())
