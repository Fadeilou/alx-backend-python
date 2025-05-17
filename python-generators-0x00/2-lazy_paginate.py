#!/usr/bin/python3
"""
Implements lazy pagination for user data.
"""
import mysql.connector
import os
from dotenv import load_dotenv

# Using connection utilities from seed.py
seed = __import__('seed')

def paginate_users(page_size, offset):
    """
    Fetches a single page of users from the database.
    Returns a list of user dictionaries.
    """
    connection = None
    cursor = None
    rows = []
    try:
        connection = seed.connect_to_prodev()
        if not connection:
            print("Failed to connect to the database for pagination.")
            return rows # Return empty list

        cursor = connection.cursor(dictionary=True)
        query = f"SELECT user_id, name, email, age FROM user_data LIMIT {page_size} OFFSET {offset}"
        cursor.execute(query)
        rows = cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error during pagination: {err}")
    except Exception as e:
        print(f"An unexpected error occurred in paginate_users: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    return rows


def lazy_pagination(page_size=100):
    """
    Generator function that lazily loads user data page by page.
    Yields one page (list of user dictionaries) at a time.
    Uses `paginate_users` to fetch data.
    Offset starts at 0.
    """
    offset = 0
    # This is the single loop allowed for lazy_pagination
    while True:
        page = paginate_users(page_size=page_size, offset=offset)
        if not page:  # No more users / empty page
            break
        yield page
        offset += page_size

if __name__ == '__main__':
    # Example usage for testing 2-lazy_paginate.py directly
    print("Testing lazy pagination (first 2 users from first 2 pages of size 3):")
    page_count = 0
    for page_num, page_data in enumerate(lazy_pagination(page_size=3)):
        if page_num >= 2: # Limit to 2 pages for test
            break
        print(f"\n--- Page {page_num + 1} ---")
        user_count_in_page = 0
        for user_in_page in page_data:
            if user_count_in_page >=2: # Limit to 2 users per page for test
                break
            print(user_in_page)
            user_count_in_page += 1
