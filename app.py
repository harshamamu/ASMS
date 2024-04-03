from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from faker import Faker  # Importing the Faker class
import pandas as pd
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, BooleanField, validators
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'Jabil123'

class RemoveServerForm(FlaskForm):
    shelf_name = StringField('Shelf Name', validators=[DataRequired()])
    submit = SubmitField('Search')

# Function to connect to the SQLite database
def connect_db():
    return sqlite3.connect('server_inventory.db', timeout=10)  # Add a timeout of 10 seconds

@app.route('/remove_servers', methods=['GET', 'POST'])
def remove_servers():
    form = RemoveServerForm()
    if request.method == 'POST':
        shelf_name = request.form['shelf_name']
        return redirect(url_for('remove_shelf', shelf_name=shelf_name))
    return render_template('remove_server.html', form=form)

@app.route('/remove_servers/<shelf_name>', methods=['GET', 'POST'])
def remove_shelf(shelf_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, asset_number, slot_number, date_in, date_out
        FROM Servers
        WHERE shelf_name = ?
    ''', (shelf_name,))
    servers = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        servers_to_remove = request.form.getlist('servers[]')
        print("Servers to remove:", servers_to_remove)
        for server_id in servers_to_remove:
            delete_server(int(server_id))
        return redirect(url_for('success'))

    return render_template('manage_shelf.html', shelf_name=shelf_name, servers=servers)

@app.route('/insert_servers', methods=['GET', 'POST'])
def add_servers():
    if request.method == 'POST':
        shelf_name = request.form['shelf_name']
        asset_numbers = request.form['asset_numbers'].split(',')
        slot_numbers = [None] * len(asset_numbers)  # Initialize slot numbers to None

        conn = connect_db()
        cursor = conn.cursor()

        for asset_number, slot_number in zip(asset_numbers, slot_numbers):
            cursor.execute('INSERT INTO Servers (asset_number, shelf_name, slot_number) VALUES (?, ?, ?)', (asset_number, shelf_name, slot_number))

        conn.commit()
        conn.close()

        flash('Servers added successfully!')
        return redirect(url_for('index'))

    # Get the list of shelves from the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT shelf_name FROM Servers')
    shelves = cursor.fetchall()
    conn.close()

    # Render the insert_servers.html template with the shelves variable
    return render_template('insert_servers.html', shelves=shelves)

    # Render the insert_servers.html template with the shelves variable
    return render_template('insert_servers.html', shelves=shelves)



@app.route('/shelf_status')
def shelf_status():
  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute('SELECT shelf_name, COUNT(*) as num_servers FROM Servers GROUP BY shelf_name')
  shelves = cursor.fetchall()
  conn.close()
  return render_template('shelf_status.html', shelves=shelves)


def delete_server(server_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Servers WHERE id=?", (server_id,))
    conn.commit()
    conn.close()


@app.route('/success')
def success():
    return render_template('success.html')

# Route for exporting data to Excel
@app.route('/export_to_excel')
def export_to_excel():
    try:
        conn = connect_db()
        df = pd.read_sql_query("SELECT * FROM Servers", conn)
        excel_file = 'server_inventory.xlsx'
        df.to_excel(excel_file, index=False)
        return f"Data exported to {excel_file}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to create the database table
def create_table():
    try:
        with connect_db() as conn:
            cursor = conn.cursor()
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
    except Exception as e:
        print(f"An error occurred while creating the table: {str(e)}")


# Function to generate fake data and insert into the database
def generate_fake_data(num_servers):
    fake = Faker()
    conn = connect_db()
    cursor = conn.cursor()

    shelf_count = 1  # Initialize shelf count
    slot_number = 1  # Initialize slot number
    servers_on_current_shelf = 0  # Initialize servers on current shelf
    
    for i in range(num_servers):
        asset_number = fake.random_int(min=1000000000, max=9999999999)  # Generate fake asset number
        
        # Calculate shelf name based on the shelf count
        shelf_name = chr(65 + shelf_count - 1) + str(servers_on_current_shelf // 25 + 1)  # A1, A2, ..., Z25, A26, A27, ..., Z50, and so on
        
        date_in = fake.date_time_between(start_date="-1y", end_date="now")  # Generate a fake date in the past year
        date_out = fake.date_time_between(start_date=date_in, end_date="now") if fake.boolean(chance_of_getting_true=50) else None  # Randomly generate a date out, if the server is removed

        # Insert data into the table
        cursor.execute('''
       ---     INSERT INTO Servers (asset_number, shelf_name, slot_number, date_in, date_out)
            VALUES (?, ?, ?, ?, ?)
        ''', (asset_number, shelf_name, slot_number, date_in, date_out))

        # Increment the server count on the current shelf
        servers_on_current_shelf += 1
        
        # If the current shelf is full (25 servers), move to the next shelf
        if servers_on_current_shelf == 25:
            shelf_count += 1
            servers_on_current_shelf = 0
            slot_number = 1  # Reset slot number for the next shelf
        else:
            slot_number += 1  # Increment slot number

    conn.commit()
    conn.close()

    print(f"Database 'server_inventory.db' created with {num_servers} entries of fake data.")




# Route for the home page (dashboard)
@app.route('/')
def index():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT shelf_name, COUNT(*) FROM Servers GROUP BY shelf_name')
    servers_by_shelf = {row[0]: row[1] for row in cursor.fetchall()}  # Using dictionary instead of list
    conn.close()
    return render_template('index.html', servers_by_shelf=servers_by_shelf)


# Route for displaying servers based on the chosen option
@app.route('/display_servers/<display_option>')
def display_servers(display_option):
    conn = connect_db()
    cursor = conn.cursor()

    if display_option == 'by_shelf':
        cursor.execute('''
            SELECT DISTINCT shelf_name
            FROM Servers
        ''')
        shelves = cursor.fetchall()
        conn.close()
        return render_template('display_servers.html', display_option='by_shelf', shelves=shelves)

    elif display_option == 'all':
        cursor.execute('''
            SELECT *
            FROM Servers
        ''')
        servers = cursor.fetchall()
        conn.close()
        return render_template('display_servers.html', display_option='all', servers=servers)

# Route to display server information grouped by shelf
@app.route('/shelf/<shelf_name>')
def shelf(shelf_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT asset_number, slot_number, date_in, date_out
        FROM Servers
        WHERE shelf_name = ?
    ''', (shelf_name,))
    servers = cursor.fetchall()
    conn.close()
    return render_template('shelf.html', shelf_name=shelf_name, servers=servers)

# Route for single asset number search
@app.route('/search_single', methods=['GET', 'POST'])
def search_single():
    if request.method == 'POST':
        asset_number = request.form['asset_number']
        location = find_server_location(asset_number)
        return render_template('result.html', location=location)
    return render_template('search_single.html')


@app.route('/search_multiple', methods=['GET', 'POST'])
def search_multiple():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded"
        
        file = request.files['file']
        
        if file.filename == '':
            return "No file selected"
        
        if file:
            asset_numbers = []
            for line in file:
                asset_number = line.decode().strip()  # Decode byte string to string and strip whitespace
                asset_numbers.append(asset_number)
            
            locations = {}
            for asset_number in asset_numbers:
                locations[asset_number] = find_server_location(asset_number)
            
            return render_template('result_multiple.html', locations=locations)
    
    return render_template('search_multiple.html')

# Function to find server location by asset number
def find_server_location(asset_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT shelf_name
        FROM Servers
        WHERE asset_number = ?
    ''', (asset_number,))
    location = cursor.fetchone()
    conn.close()
    if location:
        return location[0]
    else:
        return "Server not found"

# Route for managing the database (creating or clearing)
@app.route('/manage_database', methods=['GET', 'POST'])
def manage_database():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'create':
            num_servers = int(request.form['num_servers'])
            create_table()
            generate_fake_data(num_servers)
            return redirect(url_for('index'))
        elif action == 'clear':
            clear_database()
            return redirect(url_for('index'))
    return render_template('manage_database.html')

# Function to clear all data from the database
def clear_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Servers')
    conn.commit()
    conn.close()



if __name__ == '__main__':
    #normalize_data()  # Normalize the data in the database
    app.run(debug=True)
