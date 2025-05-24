import time
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
    print(f"Database '{db_file}' set up for 3-retry_on_failure.py.")
# --- End Database Setup ---

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

def retry_on_failure(retries=3, delay=1):
    """
    Decorator factory that retries a function call a specified number of times
    if it raises an exception.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 2): # retries + 1 attempts total
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt > retries: # Last attempt also failed
                        print(f"RETRY: All {retries} retries failed for {func.__name__}. Last error: {e}")
                        raise
                    print(f"RETRY: Attempt {attempt} for {func.__name__} failed with error: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Counter for simulating failures
failure_simulation_counter = 0

@with_db_connection
@retry_on_failure(retries=3, delay=1) # Default delay is 1s from prompt example
def fetch_users_with_retry(conn):
    global failure_simulation_counter
    cursor = conn.cursor()
    
    # Simulate a transient error for the first 2 attempts
    if failure_simulation_counter < 2:
        failure_simulation_counter += 1
        raise sqlite3.OperationalError(f"Simulated database error (attempt {failure_simulation_counter})")
    
    print("DB: Successfully executing fetch_users_with_retry.")
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

if __name__ == "__main__":
    setup_database()

    print("\nAttempting to fetch users with automatic retry on failure:")
    try:
        users = fetch_users_with_retry()
        print("Fetched users successfully:", users)
    except Exception as e:
        print(f"Main: Could not fetch users after retries. Error: {e}")

    # Test case where it always fails
    print("\nAttempting to fetch users with retry (guaranteed to fail all retries):")
    failure_simulation_counter = 0 # Reset counter
    
    @with_db_connection
    @retry_on_failure(retries=2, delay=0.5) # Custom retries/delay
    def fetch_users_always_fail(conn):
        global failure_simulation_counter
        failure_simulation_counter += 1
        raise sqlite3.OperationalError(f"Simulated persistent DB error (attempt {failure_simulation_counter})")

    try:
        fetch_users_always_fail()
    except sqlite3.OperationalError as e:
        print(f"Main: Caught expected persistent error: {e}")
