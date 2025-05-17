#!/usr/bin/python3
from itertools import islice
stream_users_func = __import__('0-stream_users').stream_users # Get the function itself

# iterate over the generator function and print only the first 6 rows

for user in islice(stream_users_func(), 6):
    print(user)
