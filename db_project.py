import mysql.connector

# Establish connection to MySQL database
db_config = {
    'host': 'localhost',      # MySQL server address (localhost if local)
    'user': 'user1',          # Your MySQL username
    'password': 'password',   # Your MySQL password
    'database': 'database_project'  # Your database name
}

# Establish the connection
try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print('Connection established successfully!')
except mysql.connector.Error as err:
    print(f"Error: {err}")
