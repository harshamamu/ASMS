import sqlite3
from faker import Faker
from random import randint, choice
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect('server_inventory.db')
cursor = conn.cursor()

# Create table to store server information
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Servers (
                    id INTEGER PRIMARY KEY,
                    asset_number INTEGER NOT NULL,
                    shelf_name TEXT NOT NULL,
                    slot_number INTEGER NOT NULL,
                    date_in DATE NOT NULL,
                    date_out DATE
                )
            ''')

# Generate fake data for 100 entries
fake = Faker()
for _ in range(100):
    asset_number = randint(1000000000, 9999999999)  # Generate fake asset number
    shelf_name = choice(['A', 'B', 'C', 'D', 'E'])  # Choose a random shelf name
    date_in = fake.date_time_between(start_date="-1y", end_date="now")  # Generate a fake date in the past year
    date_out = fake.date_time_between(start_date=date_in, end_date="now") if randint(0, 1) else None  # Randomly generate a date out, if the server is removed

    # Insert data into the table
    cursor.execute('''
        INSERT INTO Servers (asset_number, shelf_name, date_in, date_out)
        VALUES (?, ?, ?, ?)
    ''', (asset_number, shelf_name, date_in, date_out))

# Commit changes and close connection
conn.commit()
conn.close()

print("Database 'server_inventory.db' created with 100 entries of fake data.")
