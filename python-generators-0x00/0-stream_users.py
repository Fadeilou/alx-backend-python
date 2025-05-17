#!/usr/bin/python3
"""
Contains a generator function to stream users one by one from the database.
"""
import mysql.connector
import os
from dotenv import load_dotenv

# Assuming seed.py contains connect_to_prodev and DB_NAME,
# or we redefine connection logic here.
# For modularity, it's better to have a common db connection utility.
# Let's use the one from seed.py
seed = __import__('seed')


def stream_users():
    """
    Generator that connects to the ALX_prodev database
    and yields user data row by row.
    Each row is yielded as a dictionary.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            print("Failed to connect to the database for streaming users.")
            return # Exit generator if no connection

        # Using dictionary=True to get rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")

        # This is the single loop allowed
        while True:
            row = cursor.fetchone()
            if row is None:  # No more rows
                break
            yield row
            
    except mysql.connector.Error as err:
        print(f"Database error while streaming users: {err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    # Example usage for testing 0-stream_users.py directly
    from itertools import islice
    print("Streaming first 3 users:")
    for user in islice(stream_users(), 3):
        print(user)
