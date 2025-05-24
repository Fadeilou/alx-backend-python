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
    print(f"Database '{db_file}' set up for 1-with_db_connection.py.")
# --- End Database Setup ---

def with_db_connection(func):
    """
    Decorator that opens a database connection, passes it to the function,
    and closes it afterwards.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            # Pass the connection as the first argument to the decorated function
            result = func(conn, *args, **kwargs)
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            # Optionally, re-raise the exception or handle it
            raise 
        finally:
            if conn:
                conn.close()
    return wrapper

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

if __name__ == "__main__":
    setup_database()

    print("\nFetching user by ID with automatic connection handling:")
    user = get_user_by_id(user_id=1)
    print(f"Fetched user (ID 1): {user}")

    user_not_found = get_user_by_id(user_id=99)
    print(f"Fetched user (ID 99): {user_not_found}")
