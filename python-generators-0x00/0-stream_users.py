from seed import connect_to_prodev


def stream_users():
    """Stream users from the file"""
    connection = connect_to_prodev()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")

        for row in cursor:
            yield row

    finally:
        connection.close()