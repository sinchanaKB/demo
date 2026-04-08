from flask import Flask, jsonify
import pyodbc
import os

app = Flask(__name__)

# To connect from a Linux Docker container, this gets overridden by docker-compose.yml to 'host.docker.internal'.
# When running locally on Windows, it defaults to your actual server name!
DB_SERVER = os.environ.get('DB_SERVER', r'host.docker.internal,1433')
DB_NAME = os.environ.get('DB_NAME', 'employee')

def get_db_connection():
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')
    
    # If username and password are provided (like in Docker via SQL Auth), use them.
    # Otherwise, fallback to Windows Authentication (perfect for running natively).
    if db_user and db_pass:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER=host.docker.internal,1433;DATABASE=employee ;UID=sa;PWD=StrongPassword@123;TrustServerCertificate=yes;'
    else:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;'
        
    return pyodbc.connect(conn_str)

@app.route('/')
def home():
    return "SQL Server Reader App is Running! Visit http://localhost:5001/employees to view data."

@app.route('/employees')
def get_employees():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the read operation
        cursor.execute("SELECT * FROM emp")
        
        # Turn the rows into a beautiful JSON response
        columns = [column[0] for column in cursor.description]
        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return jsonify({"status": "success", "data": data})
        
    except Exception as e:
        # Returns the error so you can debug if the ODBC fails
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Binds to 0.0.0.0 so Docker can map it outwards to localhost
    app.run(host='0.0.0.0', port=5000)
