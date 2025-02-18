import sqlite3
import datetime

# Basic setup
# Connection


def connect():
    conn = sqlite3.connect('database/testdb.db')
    cursor = conn.cursor()
    return conn, cursor

# ip TEXT,
# geoloc TEXT


def create_users_table():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        ip TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('create_users_table Sucessfull')


def create_login_log_table():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS loginLog (
        id INTEGER PRIMARY KEY,
        username TEXT,
        ip TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print('create_Login_log Successful')



def insert_login_log(username, ip):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR IGNORE INTO LoginLog (username, ip, timestamp) VALUES (?, ?, ?)
    ''', (username, ip, datetime.datetime.now()))
    conn.commit()
    conn.close()


def create_table_user_data():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS userData (
        id INTEGER PRIMARY KEY,
        username TEXT,
        ip TEXT,
        country TEXT,
        regionname TEXT,
        city TEXT,
        zip TEXT, 
        lat REAL,  
        lon REAL, 
        timezone TEXT,
        isp TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('create_users_data_table Successful')


def insert_user_Data(username, ip, country, region, city, user_zip, latitude, longitude, isp, timezone):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR REPLACE INTO userData (username, ip, country, regionname, city, zip, lat, lon, timezone, isp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (username, ip, country, region, city, user_zip, latitude, longitude, timezone, isp))
    conn.commit()
    conn.close()


def create_table_likedMeals():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS likedMeals (
        id INTEGER PRIMARY KEY,
        username TEXT,
        likedMeals TEXT
    )
    ''')
    conn.commit()
    conn.close()
    print('create_table_likedMeals Successfull')


def insert_user(username, password, ip):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, ip) VALUES (?, ?, ?)
    ''', (username, password, ip))
    conn.commit()
    conn.close()


def update_password(username, password, ip):
    conn, cursor = connect()
    cursor.execute('''
    REPLACE INTO users (username, password, ip) VALUES (?, ?, ?)
''', (username, password, ip))
    cursor.execute('''
        DELETE FROM reset_tokens WHERE username = ?
    ''', (username,))
    conn.commit()
    conn.close()


def create_reset_tokens_table():
    conn, cursor = connect()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reset_tokens (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        reset_token TEXT,
        reset_token_expiry TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print('create_reset_tokens_table Successful')


def insert_reset_token(username, reset_token, reset_token_expiry):
    conn, cursor = connect()

    try:
        # Use a context manager (with statement)
        with conn:
            # Check if a token already exists for the user
            existing_token = cursor.execute('''
                SELECT reset_token 
                FROM reset_tokens 
                WHERE username = ?
            ''', (username,)).fetchone()

            if existing_token:
                # If a token exists, delete the existing record
                cursor.execute('''
                    DELETE FROM reset_tokens 
                    WHERE username = ?
                ''', (username,))

            # Insert the new token
            cursor.execute('''
                INSERT INTO reset_tokens (username, reset_token, reset_token_expiry) 
                VALUES (?, ?, ?)
            ''', (username, reset_token, reset_token_expiry))
    except Exception as e:
        # Handle the exception (e.g., log it or raise a custom exception)
        print(f"Error inserting reset token: {e}")
    finally:
        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

def get_username_from_token(token):
    conn, cursor = connect()
    cursor.execute('''
        SELECT username FROM reset_tokens WHERE reset_token = ?
    ''', (token,))
    username = cursor.fetchone()
    if username:
        return username[0]
    else: 
        return None

def get_token_details(token):
    conn, cursor = connect()
    cursor.execute('''
        SELECT * FROM reset_tokens WHERE reset_token = ?
    ''', (token,))
    data = cursor.fetchone()
    if data:
        return data
    else:
        return None




def insert_liked_Meals(username, likedMeals):
    conn, cursor = connect()
    cursor.execute('''
    INSERT OR REPLACE INTO likedMeals (username, likedMeals) VALUES (?, ?)
    ''', (username, likedMeals))
    conn.commit()
    conn.close()


def remove_liked_Meals(username, idMeal):
    conn, cursor = connect()
    # Delete rows where the username matches and likedMeals contains the specified idMeal
    cursor.execute('''
    DELETE FROM likedMeals
    WHERE username = ? AND likedMeals LIKE ?
    ''', (username, f'%{idMeal}%'))
    conn.commit()
    conn.close()


def get_user(username):
    conn, cursor = connect()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user_dict = {
            'id': user_data[0],
            'username': user_data[1],
            'password': user_data[2],
            'ip': user_data[3]
        }
        return user_dict
    else:
        return None


def get_liked_Meals_db(username):
    conn, cursor = connect()
    cursor.execute('SELECT * FROM likedMeals WHERE username = ?', (username,))
    user_liked_meals = cursor.fetchall()
    conn.commit()
    conn.close()
    return user_liked_meals

def get_user_data(username):
    conn, cursor = connect()
    # cursor.execute('SELECT * FROM userData WHERE username = ?', (username,))
    cursor.execute('''
        SELECT * FROM userData 
        WHERE username = ? 
        AND id = (SELECT MAX(id) FROM userData WHERE username = ?)
    ''', (username, username))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        user_data_dict = {
            'id': user_data[0],
            'username': user_data[1],
            'ip': user_data[2],
            'country': user_data[3],
            'regionname': user_data[4],
            'city': user_data[5],
            'zip': user_data[6],
            'lat': user_data[7],
            'lon': user_data[8],
            'timezone': user_data[9],
            'isp': user_data[10]
        }
        return user_data_dict
    else:
        return None


def get_login_log(username):
    conn, cursor = connect()
    cursor.execute('SELECT * FROM LoginLog WHERE username = ?', (username, ))
    login_log = cursor.fetchall()
    if login_log:
        login_data = [{'timestamp': log[3], 'ip': log[2]} for log in login_log]
    else:
        login_data = []
    conn.commit()
    conn.close()
    return login_data


def get_all_users():
    conn, cursor = connect()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def db():
    create_users_table()
    create_table_likedMeals()
    create_table_user_data()
    create_login_log_table()
    create_reset_tokens_table()

# Create tables
db()