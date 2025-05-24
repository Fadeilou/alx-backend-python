import sqlite3
import os

DB_NAME = 'mydatabase.db' # Consistent database name

def setup_database_task0():
    """Specific setup for Task 0, ensuring the database exists."""
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER
        )
        """)
        sample_users = [
            ('Alice Wonderland', 'alice@example.com', 30),
            ('Bob The Builder', 'bob@example.com', 45)
        ]
        cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users)
        conn.commit()
        conn.close()
        print(f"Database '{DB_NAME}' ensured/created for Task 0.")
    elif not is_table_populated(): # Check if setup is needed even if file exists
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        sample_users = [
            ('Alice Wonderland', 'alice@example.com', 30),
            ('Bob The Builder', 'bob@example.com', 45)
        ]
        # Ensure no duplicates if table exists but empty, or add if missing
        for user in sample_users:
            try:
                cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", user)
            except sqlite3.IntegrityError: # If email is unique and user exists
                pass # Skip if user already there
        conn.commit()
        conn.close()
        print(f"Database '{DB_NAME}' populated for Task 0.")


def is_table_populated():
    """Checks if the users table has data."""
    if not os.path.exists(DB_NAME):
        return False
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0


class DatabaseConnection:
    """
    A class-based context manager for handling SQLite database connections.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """
        Opens the database connection and returns the connection object.
        """
        print(f"Connecting to database: {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection.
        Handles exceptions if any occurred within the 'with' block.
        """
        if self.conn:
            if exc_type: # If an exception occurred
                print(f"An exception occurred: {exc_val}. Rolling back changes if any (SQLite auto-rolls back).")
                # For SQLite, DML statements are often auto-rolled back on error if not committed.
                # Explicit rollback isn't strictly needed unless you began a transaction.
                self.conn.rollback() # Good practice to show intent
            else:
                print("Committing changes (if any were made and not auto-committed).")
                # self.conn.commit() # Commit if changes were made (often not needed for SELECT)
            
            print(f"Closing database connection to: {self.db_name}")
            self.conn.close()
        
        # If you want to suppress an exception, return True from __exit__
        # For this task, we let exceptions propagate by returning None (or False implicitly)
        return False 

if __name__ == "__main__":
    # Ensure the database and table are set up before running the context manager
    if os.path.exists(DB_NAME): # If running multiple times, might want to clear
        os.remove(DB_NAME)
    setup_database_task0()

    print("\nUsing DatabaseConnection context manager:")
    try:
        with DatabaseConnection(DB_NAME) as conn:
            cursor = conn.cursor()
            print("Executing query: SELECT * FROM users")
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            
            if results:
                print("\nQuery Results:")
                for row in results:
                    print(row)
            else:
                print("No results found.")
        
        print("\n--- Example with an error (simulated) ---")
        # with DatabaseConnection(DB_NAME) as conn_error:
        #     cursor = conn_error.cursor()
        #     print("Executing faulty query...")
        #     cursor.execute("SELECT * FROM non_existent_table") # This will raise an error
        #     print("This line will not be reached.")

    except sqlite3.Error as e:
        print(f"A SQLite error occurred outside the __exit__ handling (or re-raised): {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
