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
    sample_users = [
        (1, 'Alice Smith', 'alice.smith@example.com'),
        (2, 'Bob Johnson', 'bob.johnson@example.com'),
        (3, 'Crawford Cartwright', 'initial_crawford@example.com') # For update
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?)", sample_users)
    conn.commit()
    conn.close()
    print(f"Database '{db_file}' set up for 2-transactional.py.")
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

def transactional(func):
    """
    Decorator that ensures a function's database operations are wrapped
    inside a transaction. Commits on success, rolls back on error.
    Assumes the first argument to the wrapped function is the database connection.
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs): # conn is passed by with_db_connection
        try:
            # For SQLite, transactions are often implicit for single statements.
            # Explicit transaction management:
            # conn.execute("BEGIN TRANSACTION") # Or rely on default behavior for simple cases
            print(f"TRANSACTION: Starting for {func.__name__}")
            result = func(conn, *args, **kwargs)
            conn.commit()
            print(f"TRANSACTION: Committed for {func.__name__}")
            return result
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"TRANSACTION: Rolled back for {func.__name__} due to error: {e}")
            raise # Re-raise the exception so it can be handled further up if needed
    return wrapper


@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
    # To test rollback, uncomment the line below to simulate an error
    # if user_id == 1: raise ValueError("Simulated error after update")
    print(f"DB: Email for user_id {user_id} updated to {new_email} (pending commit/rollback).")

@with_db_connection
def get_user_email(conn, user_id): # Helper to verify
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None

if __name__ == "__main__":
    setup_database()

    print("\nUpdating user's email with automatic transaction handling:")
    user_id_to_update = 3
    new_email_val = 'Crawford_Cartwright@hotmail.com'
    
    print(f"Initial email for user {user_id_to_update}: {get_user_email(user_id=user_id_to_update)}")
    update_user_email(user_id=user_id_to_update, new_email=new_email_val)
    print(f"Email after successful update for user {user_id_to_update}: {get_user_email(user_id=user_id_to_update)}")

    # Test rollback (manual setup needed for this specific scenario)
    print("\nTesting rollback scenario (simulated error):")
    user_id_fail = 1
    new_email_fail = 'fail_update@example.com'
    print(f"Initial email for user {user_id_fail}: {get_user_email(user_id=user_id_fail)}")
    
    @with_db_connection
    @transactional
    def update_user_email_and_fail(conn, user_id, new_email):
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
        print(f"DB: Email for user_id {user_id} updated to {new_email} (pending commit/rollback).")
        raise ValueError("Simulated error to trigger rollback!")

    try:
        update_user_email_and_fail(user_id=user_id_fail, new_email=new_email_fail)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    
    print(f"Email after failed update attempt for user {user_id_fail}: {get_user_email(user_id=user_id_fail)}")
