import asyncio
import aiosqlite # Asynchronous SQLite library
import os
import sqlite3 # For synchronous setup

DB_NAME = 'mydatabase.db' # Consistent database name

def setup_database_task3():
    """Synchronous setup for Task 3, as aiosqlite uses standard SQLite files."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME) # Use synchronous sqlite3 for setup
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
        ('Bob The Builder', 'bob@example.com', 45),    # Older than 40
        ('Charlie Chaplin', 'charlie@example.com', 25),
        ('Diana Prince', 'diana@example.com', 55),     # Older than 40
        ('Eve Harrington', 'eve@example.com', 38)
    ]
    cursor.executemany("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", sample_users)
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' created and populated for Task 3 (async operations).")


async def async_fetch_users(db_path):
    """Fetches all users asynchronously."""
    print("Starting async_fetch_users...")
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT id, name, age FROM users") as cursor:
            results = await cursor.fetchall()
            print("async_fetch_users completed.")
            return results

async def async_fetch_older_users(db_path, age_threshold):
    """Fetches users older than a given age threshold asynchronously."""
    print(f"Starting async_fetch_older_users (age > {age_threshold})...")
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT id, name, age FROM users WHERE age > ?", (age_threshold,)) as cursor:
            results = await cursor.fetchall()
            print(f"async_fetch_older_users (age > {age_threshold}) completed.")
            return results

async def fetch_concurrently(db_path):
    """
    Uses asyncio.gather() to execute both fetch queries concurrently.
    """
    print("Starting concurrent fetching...")
    # asyncio.gather runs multiple awaitables (coroutines) concurrently
    # It returns a list of results in the same order as the input awaitables
    all_users_task = async_fetch_users(db_path)
    older_users_task = async_fetch_older_users(db_path, 40)
    
    # The results will be a list: [result_from_all_users_task, result_from_older_users_task]
    results_list = await asyncio.gather(
        all_users_task,
        older_users_task
    )
    print("Concurrent fetching completed.")
    return results_list


if __name__ == "__main__":
    setup_database_task3() # Setup the database first

    print("\nRunning concurrent database queries using asyncio.gather:")
    
    # asyncio.run() is the main entry point to run an async function
    # It creates an event loop, runs the coroutine, and closes the loop.
    all_results = asyncio.run(fetch_concurrently(DB_NAME))
    
    all_users = all_results[0]
    older_users = all_results[1]

    print("\n--- All Users ---")
    if all_users:
        for user in all_users:
            print(user)
    else:
        print("No users found.")

    print("\n--- Users Older Than 40 ---")
    if older_users:
        for user in older_users:
            print(user)
    else:
        print("No users older than 40 found.")
