from seed import connect_to_prodev

def stream_users_in_batches(batch_size):
    """Stream users in batches"""
    connection = connect_to_prodev()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        batch = []
        for row in cursor:
            batch.append(row)
            if len(batch) == batch_size:
                yield batch
                batch = []

        if batch:
            yield batch
    finally:
        connection.close()
        return

def batch_processing(batch_size):
    """Process users in batches"""
    for batch in stream_users_in_batches(batch_size):
        filtered_batch = [user for user in batch if int(user['age']) > 25]
        for user in filtered_batch:
            print(user)