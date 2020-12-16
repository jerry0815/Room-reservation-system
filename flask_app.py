from flask import Flask, request , render_template
import os

import pymysql
import pymysql.cursors


app = Flask(__name__)

# Connect to the database
connection = pymysql.connect(host=os.environ.get('CLEARDB_DATABASE_HOST'),
                             user=os.environ.get('CLEARDB_DATABASE_USER'),
                             password=os.environ.get('CLEARDB_DATABASE_PASSWORD'),
                             db=os.environ.get('CLEARDB_DATABASE_DB'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

"""
with connection.cursor() as cursor:
    # Create a new record
    sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
    cursor.execute(sql, ('12/17@gmail.com', 'QQQQQQ'))

connection.commit()
"""

@app.route('/')
def hello():
    """
    with connection.cursor() as cursor:
        # Read a single record
        sql = "SELECT `id`, `email` FROM `users` WHERE `email`=%s"
        cursor.execute(sql, ('jerry.com',))
        result = cursor.fetchone()
        print(result)
    return f'Hello, Heroku {result["email"]}!'
    """
    return render_template("index.html")

if __name__ == 'main':
    app.debug = True
    app.run() #啟動伺服器