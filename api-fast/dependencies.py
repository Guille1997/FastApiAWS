from mysql.connector import connect, Error

def get_db():
    try:
        return connect(host='localhost', database='users', user='root', password='root')
    except Error as e:
        print(e)

def test_connection():
    # Get a database connection
    connection = get_db()
    if connection:
        print("Database connection established successfully.")
        
        try:
            # Execute a sample query
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users")
            
            # Fetch and print results
            rows = cursor.fetchall()
            for row in rows:
                print(row)
                
        except Error as e:
            print("Error executing query:", e)
            
        finally:
            # Close cursor and connection
            if cursor:
                cursor.close()
            connection.close()
            print("Database connection closed.")

    else:
        print("Failed to establish database connection.")

# Call the test_connection function to execute it
test_connection()
