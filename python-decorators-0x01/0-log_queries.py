import sqlite3
import functools
import os

# --- Database Setup (same as above, simplified for brevity here) ---
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
    print(f"Database '{db_file}' set up for 0-log_queries.py.")
# --- End Database Setup ---

def log_queries(func):
    """
    Decorator that logs the SQL query before executing the function.
    Assumes the first argument to the decorated function is the query string.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query_arg = ""
        # Try to find the query string in args or kwargs
        if args:
            query_arg = args[0] # Assuming query is the first positional argument
        elif 'query' in kwargs:
            query_arg = kwargs['query']
        
        if isinstance(query_arg, str):
            print(f"LOG: Executing query: {query_arg}")
        else:
            # Fallback if query extraction is not straightforward
            print(f"LOG: Executing function {func.__name__} with args: {args}, kwargs: {kwargs}. Could not identify query string.")

        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    # This function as provided in the prompt connects and closes.
    # For consistency with later tasks, this might be refactored,
    # but sticking to the prompt's structure for this task.
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    setup_database()
    
    print("\nFetching users while logging the query:")
    users = fetch_all_users(query="SELECT * FROM users")
    # print("Fetched users:", users) # Optional: print results
    
    # Example with a different query call to test argument inspection
    # users_by_name = fetch_all_users("SELECT * FROM users WHERE name = 'Alice Smith'")
