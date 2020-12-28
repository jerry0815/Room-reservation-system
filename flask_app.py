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

def insertUser():
        sql = "INSERT INTO `users` (`userName`, `nickName`,`password` , `email` , `identity` , `banned`) VALUES (%s,%s,%s,%s,%s,%s)"
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,("jerry","lulala","123456798","jerry@gmail.com",'0','0'))
            connection.commit()
def insertClassroom():
    sql = "INSERT INTO `classroom` (`building`, `roomname` , `capacity`) VALUES (%s, %s , %s)"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,("TR","TR-309","50"))
        connection.commit()

def showClassroom():
    sql = "SELECT * FROM `Classroom`"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    print(result)
    return result

def getUser(userName):
    sql = "SELECT `id`, `email`,`name`FROM `Account` WHERE `userName`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
        result = cursor.fetchone()
    print(result)
    return result

def show():
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES")
        for x in cursor:
            print(x)
"""
with connection.cursor() as cursor:
    # Create a new record
    sql = "INSERT INTO `Account` (`email`, `password` , `name`) VALUES (%s, %s , %s)"
    cursor.execute(sql, ('alien@gmail.com', 'QQQQQQ' , 'Alien'))

connection.commit()
"""
insertClassroom()
showClassroom()

@app.route('/',methods=['POST','GET'])
def hello():
    if request.method =='POST':
        if request.values['send']=='Search':
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT `id`, `email`,`name`FROM `Account` WHERE `email`=%s"
                cursor.execute(sql, (request.values['user']))
                result = cursor.fetchone()
                if result == None:
                    return render_template("index.html",name="" , id="")
                return render_template('index.html',name=result["name"] , id = result["id"])
        elif request.values['send']=='Register':
            return redirect(url_for('register'))
    return render_template("index.html",name="" , id="")

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method =='POST':
        if request.values['send']=='Submit':
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                sql = "INSERT INTO `Account` (`email`, `password` , `name`) VALUES (%s, %s , %s)"
                cursor.execute(sql, (request.values['email'], request.values['pwd'] , request.values['name']))
            connection.commit()
            return redirect(url_for('hello'))
    return render_template("register.html")

@app.route('/testDB',methods=['POST','GET'])
def testDB():
    return render_template("testDB.html")

if __name__ == '__main__':
    app.debug = True
    app.run() #啟動伺服器