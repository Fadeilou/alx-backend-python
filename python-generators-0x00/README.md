# Python Generators Project - 0x00

This project explores the use of Python generators for efficient data handling, particularly with large datasets and database interactions.

## Tasks

### 0. Getting started with python generators (seed.py)
This task involves setting up a MySQL database named `ALX_prodev`, creating a `user_data` table, and populating it with data from `user_data.csv`.

**Files:**
- `seed.py`: Contains functions to connect to MySQL, create the database and table, and insert data.
- `0-main.py`: Test script to run the seeding process.
- `user_data.csv`: Sample data file.
- `.env`: (Not committed) Stores database credentials.

**Setup:**
1. Ensure MySQL server is running.
2. Create a `.env` file with `DB_HOST`, `DB_USER`, `DB_PASSWORD`.
3. Install dependencies: `pip install mysql-connector-python python-dotenv`.
4. Place `user_data.csv` in the project root.
5. Run `chmod +x 0-main.py seed.py`
6. Execute `./0-main.py` to seed the database.
