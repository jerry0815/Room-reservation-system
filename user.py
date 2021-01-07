from os import O_RSYNC
import pymysql
from connect import connection

def insertUser(userName = "jerry", nickName = "", password = "123456798", email = "jerry@gmail.com", identity = '0' , banned = False):
    if nickName == "":
        nickName = userName
    sql = "INSERT INTO `users` (`userName`, `nickName`,`password` , `email` , `identity` , `banned`) VALUES (%s,%s,%s,%s,%s,%s)"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,(userName , nickName , password , email,identity , banned))
        connection.commit()

def isValidMail(email):
    after = email.split('@')[1]
    if after == 'gmail.com' or after == 'gapps.ntust.edu.tw':
        return True
    else:
        return False

def register(data):
    email = data['email'] + "@gmail.com"
    if not isValidMail(email):
        return False
    sql = "select * from  `users` where `userName`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,data['userName'])
        connection.commit()
        result = cursor.fetchone()
    if result != None:
        return False
    insertUser(userName = data['userName'], nickName = "", password = data['password'], email = email, identity = '0' , banned = False)
    return True

#login and return user information. return status,result
#status:
# 0:success 1:wrong email 2:wrong passward
def validateLogin(email , password):
    if email == "" or email == None:
        return (1 , None)
    sql = "SELECT * FROM `users` WHERE `email` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        connection.commit()
        result = cursor.fetchone()
    #1 : wrong email
    if result == None:
        return (1 , None)
    #2 : wrong passward
    if result["password"] != password:
        return (2,None)
    else:
        return (0,result['userName'])

#for cookie
def loginCheck(email : str ,password : str):
    if email == "" or email == None:
        return (False,None)
    sql = "SELECT `password` , `identity` FROM `users` WHERE `email` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        connection.commit()
        result = cursor.fetchone()
    #wrong email
    if result == None:
        return (False,None)
    #wrong passward
    if result["password"] != password:
        return (False,None)
    else:
        if result["identity"] == 0:
            admin = 'normal'
        else:
            admin = 'admin'
        return (True,admin)

#modify user's nickname 
def modifyNickName(userName , nickName):
    sql = " UPDATE `users` SET nickName = %s WHERE userName = %s "
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql , (nickName,userName))
        connection.commit()

def deleteAccount(userID):
    sql = "DELETE FROM `users` WHERE `userID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userID)
        connection.commit()
    return True

def banAccount(userID):
    sql = " UPDATE `users` SET `banned` = %s WHERE `userID` = %s "
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql , (True , userID))
        connection.commit()
    return True

def unBanAccount(userID):
    sql = " UPDATE `users` SET `banned` = %s WHERE `userID` = %s "
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql , (False , userID))
        connection.commit()
    return True

def getAllUserName():
    sql = "SELECT `userName` FROM `users`"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()
        result = cursor.fetchall()

    for i in range(len(result)):
        result[i] = result[i]['userName']
    return result
#display all users
def showUsers():
    sql = "SELECT * FROM users"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()
        result = cursor.fetchall()
    print(result)
    return result

# return all information about users ["userID","userName", "nickName","password" , "email" , "identity" , "banned"]
def getUser(userName):
    sql = "SELECT * FROM `users` WHERE `userName`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
        connection.commit()
        result = cursor.fetchone()
    if result == None:
        return (False,None)
    result = dict(result)
    if int(result['banned']) == 1:
        result['banned'] = True
    elif int(result['banned']) == 0:
        result['banned'] = False
    else :
        print("error")
    return (True , result)

def getUserMail(userName):
    if userName == None or len(userName) == 0:
        return []
    sql = "SELECT `email` FROM `users` WHERE `userName` IN ({seq})".format(seq=','.join(['%s']*len(userName)))
    print(sql)
    print(userName)
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
        connection.commit()
        results = cursor.fetchall()
    if results == None:
        return []
    email_list = []
    for result in results:
        email_list.append(result['email'])
    return email_list
