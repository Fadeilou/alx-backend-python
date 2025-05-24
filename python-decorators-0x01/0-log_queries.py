import sqlite3
import functools
import os
from datetime import datetime # Import datetime

# --- Database Setup ---
def setup_database():
    db_file = 'users.db'
    # Remove existing database file to ensure a fresh start
    if os.path.exists(db_file):
        os.remove(db_file)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # Create users table
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    """)
    # Insert some sample data
    sample_users = [
        ('Alice Smith', 'alice.smith@example.com'),
        ('Bob Johnson', 'bob.johnson@example.com')
    ]
    cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", sample_users)
    conn.commit()
    conn.close()
    # print(f"Database '{db_file}' set up for 0-log_queries.py.") # Optional: for local testing
# --- End Database Setup ---

def log_queries(func):
    """
    Decorator that logs the SQL query with a timestamp before executing the function.
    Assumes the query string is the first positional argument or a keyword argument 'query'.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query_arg = None
        
        # Attempt to find the query string.
        # Check kwargs first, then positional args.
        # The prompt's example shows `fetch_all_users(query="SELECT * FROM users")`
        # which means 'query' will be in kwargs if called like that,
        # or in args if called as `fetch_all_users("SELECT * FROM users")`.
        
        if 'query' in kwargs:
            query_arg = kwargs['query']
        elif args:
            # Assuming the query is the first argument if not in kwargs.
            # This needs to be robust if the decorated function takes other positional args before 'query'.
            # For `fetch_all_users(query)`, query is the first and only arg.
            if isinstance(args[0], str): # Basic check if the first arg is a string
                 query_arg = args[0]

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if query_arg and isinstance(query_arg, str):
            print(f"{timestamp} LOG: Executing query: {query_arg}")
        else:
            # Fallback if query string isn't found as expected
            print(f"{timestamp} LOG: Executing function {func.__name__}. Could not identify specific query string from args/kwargs.")
            # For robustness, you might log all args/kwargs here if needed:
            # print(f"{timestamp} LOG: Executing function {func.__name__} with args: {args}, kwargs: {kwargs}. Could not identify query string.")


        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query): # As per prompt, query is the argument
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query) # The 'query' variable is used here
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    setup_database() # Ensure the database is ready
    
    print("\nFetching users (call with keyword argument 'query'):")
    users_kwarg = fetch_all_users(query="SELECT * FROM users")
    # print("Fetched users (kwarg):", users_kwarg) # Optional

    print("\nFetching users (call with positional argument):")
    users_arg = fetch_all_users("SELECT name FROM users WHERE id = 1")
    # print("Fetched users (arg):", users_arg) # Optional
