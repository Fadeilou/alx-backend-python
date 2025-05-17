#!/usr/bin/python3
"""
Uses a generator to compute memory-efficient average age from user data.
"""
import mysql.connector
import os
from dotenv import load_dotenv

# Using connection utilities from seed.py
seed = __import__('seed')


def stream_user_ages():
    """
    Generator that yields user ages one by one from the database.
    """
    connection = None
    cursor = None
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            print("Failed to connect to the database for streaming ages.")
            return

        # Fetch only the age column
        cursor = connection.cursor() # No dictionary needed, just one value
        cursor.execute("SELECT age FROM user_data")

        # Loop 1: Fetching ages
        while True:
            row = cursor.fetchone()
            if row is None:  # No more rows
                break
            yield row[0]  # Yield the age value
            
    except mysql.connector.Error as err:
        print(f"Database error while streaming ages: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in stream_user_ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def calculate_average_age():
    """
    Calculates the average age of users using the stream_user_ages generator.
    Prints the result.
    """
    total_age = 0
    user_count = 0

    # Loop 2: Iterating through ages from the generator
    for age in stream_user_ages():
        total_age += age
        user_count += 1
    
    if user_count > 0:
        average_age = total_age / user_count
        print(f"Average age of users: {average_age:.2f}") # Format to 2 decimal places
    else:
        print("No users found to calculate average age.")

if __name__ == '__main__':
    calculate_average_age()
