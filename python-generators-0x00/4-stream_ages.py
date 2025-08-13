from seed import connect_to_prodev


def stream_user_ages():
    """
    Stream user ages.
    """
    connection = connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")
    while True:
        row = cursor.fetchone()
        if not row:
            break
        yield int(row['age'])
    connection.close()

def average_age():
    """
    Compute the average age.
    """
    ages = stream_user_ages()
    total = 0
    count = 0
    for age in ages:
        total += age
        count += 1
    print(f"Average age of users: {round(total / count, 2)}")

if __name__ == "__main__":
    average_age()