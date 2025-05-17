#!/usr/bin/python3
"""
Contains functions to fetch users in batches and process them.
"""
import mysql.connector
import os
from dotenv import load_dotenv

# Using connection utilities from seed.py
seed = __import__('seed')

def stream_users_in_batches(batch_size=50):
    """
    Generator that fetches users from the database in batches.
    Yields a list of user dictionaries for each batch.
    """
    connection = None
    cursor = None
    offset = 0
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            print("Failed to connect to the database for batch streaming.")
            return

        cursor = connection.cursor(dictionary=True)
        
        # Loop 1: Fetching batches
        while True:
            query = f"SELECT user_id, name, email, age FROM user_data LIMIT {batch_size} OFFSET {offset}"
            cursor.execute(query)
            batch = cursor.fetchall()
            
            if not batch:  # No more users
                break
            
            yield batch
            offset += batch_size
            
    except mysql.connector.Error as err:
        print(f"Database error during batch streaming: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in stream_users_in_batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def batch_processing(batch_size=50):
    """
    Processes users in batches, filtering for users over the age of 25.
    Prints the filtered users.
    """
    # Loop 2: Iterating over batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 3: Iterating over users within a batch
        for user in batch:
            if user['age'] > 25:
                print(user) # As per example, it prints. Could also yield.

if __name__ == '__main__':
    # Example usage for testing 1-batch_processing.py directly
    print("Processing users in batches (first few results for users > 25):")
    # This will print a lot, so typically you'd pipe it or limit output
    # For direct testing, let's just call it and expect output.
    # The 2-main.py will pipe to head.
    try:
        batch_processing(5) # Using a small batch for direct test
    except BrokenPipeError:
        # This can happen if output is piped and the pipe closes (e.g., `| head`)
        import sys
        sys.stderr.close()
