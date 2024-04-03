import sqlite3

# Connect to the database
conn = sqlite3.connect('server_inventory.db')
cursor = conn.cursor()

# Execute a SQL query to fetch a single row (change the condition as per your requirement)
#cursor.execute("SELECT * FROM Servers WHERE asset_number = ?", (8613497696,))
#row = cursor.fetchone()

# Execute a SQL query to fetch the first 25 rows
cursor.execute("SELECT * FROM Servers LIMIT 25")
rows = cursor.fetchall()


# Print or display the row
print(rows)

# Close the connection
conn.close()
