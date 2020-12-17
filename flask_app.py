from flask import Flask, request , render_template , redirect , url_for
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

while True:
    try:
        connection.ping()
        break
    except:
        connection.ping(True)

with connection.cursor() as cursor:
    # Create a new record
    sql = "INSERT INTO `Account` (`email`, `password` , `name`) VALUES (%s, %s , %s)"
    cursor.execute(sql, ('alien@gmail.com', 'QQQQQQ' , 'Alien'))

connection.commit()


@app.route('/',methods=['POST','GET'])
def hello():
    if request.method =='POST':
        if request.values['send']=='Search':
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `id`, `email`,`name`FROM `Account` WHERE `email`=%s"
                cursor.execute(sql, (request.values['user']))
                result = cursor.fetchone()
                print(result)
                return render_template('index.html',name=result["name"] , id = result["id"])
        elif request.values['send']=='Register':
            redirect(url_for('register'))
    return render_template("index.html",name="")

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method =='POST':
        if request.values['send']=='Submit':
            with connection.cursor() as cursor:
                sql = "INSERT INTO `Account` (`email`, `password` , `name`) VALUES (%s, %s , %s)"
                cursor.execute(sql, (request.values['email'], request.values['password'] , request.values['name']))
                result = cursor.fetchone()
            return render_template('index.html',name=result["name"] , id = result["id"])
    return render_template("register.html")
if __name__ == '__main__':
    app.debug = True
    app.run() #啟動伺服器