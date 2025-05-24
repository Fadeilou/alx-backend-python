import sqlite3
import os

DB_NAME = 'mydatabase.db' # Consistent database name

def setup_database_task1():
    """Specific setup for Task 1, ensuring the database exists with age column."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        age INTEGER
    )
    """)
    sample_users = [
        ('Alice Wonderland', 'alice@example.com', 30),
        ('Bob The Builder', 'bob@example.com', 45),
        ('Charlie Chaplin', 'charlie@example.com', 25), # Will not be > 25
        ('Diana Prince', 'diana@example.com', 55)    # Will be > 25
    ]
    cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users)
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' created and populated for Task 1.")


class ExecuteQuery:
    """
    A reusable context manager that takes a query and parameters,
    executes it, and returns the results.
    """
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params if params is not None else () # Default to empty tuple for no params
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Opens connection, creates cursor, executes query, and returns results.
        """
        print(f"Connecting to database: {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        print(f"Executing query: {self.query} with params: {self.params}")
        self.cursor.execute(self.query, self.params)
        results = self.cursor.fetchall()
        return results

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the cursor and the connection.
        """
        if self.cursor:
            print("Closing cursor.")
            self.cursor.close()
        if self.conn:
            if exc_type:
                print(f"An exception occurred: {exc_val}. Rolling back.")
                self.conn.rollback()
            else:
                # Committing isn't usually necessary for SELECT queries,
                # but good practice if the context manager could also handle INSERT/UPDATE.
                # For this task, it's a SELECT, so commit is optional.
                # print("Committing transaction (if applicable).")
                # self.conn.commit()
                pass

            print(f"Closing database connection to: {self.db_name}")
            self.conn.close()
        
        # Let exceptions propagate
        return False

if __name__ == "__main__":
    setup_database_task1()

    query_str = "SELECT * FROM users WHERE age > ?"
    parameters = (25,) # Parameters must be a tuple

    print(f"\nUsing ExecuteQuery context manager for query: '{query_str}' with params {parameters}")
    try:
        with ExecuteQuery(DB_NAME, query_str, parameters) as results:
            if results:
                print("\nQuery Results (users older than 25):")
                for row in results:
                    print(row)
            else:
                print("No users found matching the criteria.")
        
        print("\n--- Example with no parameters (SELECT all) ---")
        with ExecuteQuery(DB_NAME, "SELECT name, email FROM users") as all_users_results:
            if all_users_results:
                print("\nQuery Results (all users name, email):")
                for row in all_users_results:
                    print(row)
            else:
                print("No users found.")

    except sqlite3.Error as e:
        print(f"A SQLite error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
