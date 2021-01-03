from datetime import datetime , timedelta
import pytz
import os
import re
import pymysql
import pandas as pd

# Connect to the database
connection = pymysql.connect(host=os.environ.get('CLEARDB_DATABASE_HOST'),
                             user=os.environ.get('CLEARDB_DATABASE_USER'),
                             password=os.environ.get('CLEARDB_DATABASE_PASSWORD'),
                             db=os.environ.get('CLEARDB_DATABASE_DB'),
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

#======================================================================
#user table
#insert user into database userName , nickName , password , email , identity , banned
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
    if not isValidMail(data['email']):
        return False
    sql = "select * from  `users` where `userName`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,data['userName'])
        result = cursor.fetchone()
    if result != None:
        return False
    insertUser(userName = data['userName'], nickName = "", password = data['password'], email = data['email'], identity = '0' , banned = False)
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

#display all users
def showUsers():
    sql = "SELECT * FROM users"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    print(result)
    return result

# return all information about users ["userID","userName", "nickName","password" , "email" , "identity" , "banned"]
def getUser(userName):
    sql = "SELECT * FROM `users` WHERE `userName`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
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
#=======================================================================

#=======================================================================
#classroom table
#insert some default classroom
def insertClassroom():
    record = []
    sql = "INSERT INTO `classroom` (`building`, `roomname` , `capacity`) VALUES (%s, %s , %s)"
    build = ["TR" , "T4" , "RB" , "IB" , "EE"]
    for b in build:
        for story in range(2,5):
            for i in range(5,8):
                name = b + "-" + str(story) + "0" + str(i)
                l = [b , name , "50"]
                record.append(l)
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.executemany(sql,record)
        connection.commit()

#display all classroom
def showClassroom():
    sql = "SELECT * FROM Classroom"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    print(result)
    return result
#=======================================================================

#=======================================================================
#transform list of id to str O
def listIdToStr(id_list):
    participant = str(id_list[0])
    for i in range(1 , len(id_list)):
        participant = participant + "," + str(id_list[i])
    return participant

#insert record O
def insertRecord(title = "testing record", roomname  = "TR-306", startDate = "2020-12-30", startSection  = "5", \
    endDate = "2020-12-30", endSection  = "8", participant = ['jerry','alien','wacky'], bookName = "jerry",type = "0"):

    #get booker userid
    sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,bookName)
        B_ID = cursor.fetchone()["userID"]

    #get classroom CR_ID
    sql = "SELECT  `CR_ID` FROM `classroom` WHERE `roomname`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,roomname)
        CR_ID = cursor.fetchone()["CR_ID"]
    print("CR_ID = "  + str(CR_ID))
    #process participant
    p_id = []
    sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
    for ppl in participant:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,ppl)
            result = cursor.fetchone()["userID"]
            p_id.append(result)
    p_id_str = listIdToStr(p_id)
    print("p_id_str = " + str(p_id_str))
    #insert record into database
    sql = "INSERT INTO `record` (`title`, `CR_ID`,`startDate` , `startSection` , `endDate` , `endSection` , `participant` ,  `B_ID` , `type`) \
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,(title,CR_ID,startDate , startSection , endDate, endSection , p_id_str , B_ID,type))
        connection.commit()

#XX not for front-end , return dict of records(one section one record) retrun none if date not match
def processRecord(record,date):
    if str(record["startDate"]) != date:
        return None
    if record["startDate"] < record["endDate"]:
        endSection = 14
    else :
        endSection = record["endSection"]
    recordDict = {}
    for i in range(record["startSection"] , endSection + 1):
        #type , title , bookerName
        sql = "SELECT  `userName` FROM `users` WHERE `userID`= %s"
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,record["B_ID"])
            name = cursor.fetchone()["userName"]
        recordDict[i] = (record["type"],record["title"] , name)
    return recordDict

#give the condition to search classroom
#parameter (building ,capacity ,roomname ,date)
def searchClassroom(building, capacity = -1 , roomname = "" , date = "2020-01-01"):
    if roomname != None and roomname != "":
        if  building != "":
            if roomname[0:2] != building:
                return None
        if  capacity != None and capacity != "" and int(capacity) > 0:
            sql = "SELECT * FROM classroom WHERE `roomname` = %s AND `capacity` > %s"
            condition = (roomname,capacity)
        else:
            sql = "SELECT * FROM classroom WHERE `roomname` = %s"
            condition = roomname
    else:
        if capacity != None and capacity != "" and int(capacity) > 0:
            if building != "":
                sql = "SELECT * FROM classroom WHERE `building` = %s AND `capacity` > %s"
                condition = (building,capacity)
            else:
                sql = "SELECT * FROM classroom WHERE `capacity` > %s"
                condition = capacity
        elif building != "":
            sql = "SELECT * FROM classroom WHERE `building` = %s"
            condition = building
        else:
            print("no condition")
    print(condition)
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,condition)
        result = cursor.fetchall()
    output = []
    sql = "SELECT * FROM record WHERE `CR_ID` = %s AND `startDate` = %s"
    print(result)
    for i in result:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,(i["CR_ID"],date))
            tmp = cursor.fetchall()
            if tmp != ():
                for j in tmp:
                    item = processRecord(j , date)
                    #building , capacity , roomname , status
                    item = {"CR_ID" : i["CR_ID"] , "building" : i["building"] , "capacity" : i["capacity"] , "roomName" : i["roomname"] , "status" : item}
                    output.append(item)          
    return output

#search for one classroom and return records of a week
# return format:  dict{ 'CR_ID' : CR_ID ,'building' : building , 'capacity' : capacity , 'roomName' : roomname , 'status' : dict{id : tuple()}(7days) }
#parameter (classroom name , date of the week)
def searchOneClassroom(CR_ID = "" , date = "2020-12-29") :
    sql = "SELECT * FROM classroom WHERE `CR_ID` = %s"
    with connection.cursor() as cursor:
        cursor.execute(sql,CR_ID)
        result = cursor.fetchone()
    building = result["building"]
    capacity = result["capacity"]
    roomname = result["roomname"]
    today = datetime.fromisoformat(date)
    n = today.weekday()
    delta = timedelta(days = n)
    startDay = str((today - delta).date())
    delta = timedelta(days = 6 - n)
    endDay = str((today + delta).date())
    print(startDay + " ~ " + endDay)
    sql = "SELECT * FROM record WHERE `CR_ID` = %s AND `startDate` >= %s AND `endDate` <= %s"
    output = []
    with connection.cursor() as cursor:
        cursor.execute(sql,(CR_ID,startDay,endDay))
        tmp = cursor.fetchall()
        if tmp != ():
            for d in range(0,7):
                delta = timedelta(days = n - d)
                dailyItem = {}
                for j in tmp:
                    item = processRecord(j,str((today - delta).date()))
                    if item != None:
                        dailyItem.update(item)
                output.append(dailyItem)  
            return {'CR_ID' : CR_ID , 'building' : building , 'capacity' : capacity , 'roomName' :roomname , 'status' :output}

#search the records the user book
def getRecordByBooker(userName):
    sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
        B_ID = cursor.fetchone()["userID"]

    sql = "SELECT  * FROM `record` WHERE `B_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,B_ID)
        results = cursor.fetchall()
    sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"
    for result in results:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql2,result['CR_ID'])
            tmp = cursor.fetchone()
        result['roomName'] = tmp
        p_name = []
        participants = result['participant']
        participants = participants.split(',')
        for i in participants:
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                cursor.execute(sql1,i)
                tmp = cursor.fetchone()
                if tmp != None:
                    p_name.append(tmp['userName'])
                else :
                    print(i)
        result['participant'] = p_name
    return results

#search the records the user's email book
def getRecordByBookerEmail(email):
    sql = "SELECT  `userID` FROM `users` WHERE `email`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        B_ID = cursor.fetchone()["userID"]

    sql = "SELECT  * FROM `record` WHERE `B_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,B_ID)
        results = cursor.fetchall()
    sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"
    for result in results:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql2,result['CR_ID'])
            tmp = cursor.fetchone()
        result['roomName'] = tmp['roomname']
        p_name = []
        participants = result['participant']
        participants = participants.split(',')
        for i in participants:
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                cursor.execute(sql1,i)
                tmp = cursor.fetchone()
                if tmp != None:
                    p_name.append(tmp['userName'])
                else :
                    print(i)
        result['participant'] = p_name
    return results

#get the record by id
def getRecordById(id):
    sql = "SELECT * FROM `record` WHERE `recordID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,id)
        result = cursor.fetchone()
    if result == None:
        print("no id of this result")
        return None
    sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql2,result['CR_ID'])
        tmp = cursor.fetchone()
    result['roomName'] = tmp['roomname']
    p_name = []
    participants = result['participant']
    participants = participants.split(',')
    for i in participants:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql1,i)
            tmp = cursor.fetchone()
            if tmp != None:
                p_name.append(tmp['userName'])
            else :
                print(i)
    result['participant'] = p_name
    return result

#update record by record id
def updateRecord(recordID , title ,participants):
    if title != None and title != "":
        sql = "UPDATE `record` SET `title` = %s WHERE `recordID` = %s"
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,(title,recordID))
            connection.commit()
    if participants != None:
        p_id = []
        sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
        for ppl in participants:
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                cursor.execute(sql,ppl)
                result = cursor.fetchone()["userID"]
                p_id.append(result)
        p_id_str = listIdToStr(p_id)
        sql = "UPDATE `record` SET `participant` = %s WHERE `recordID` = %s"
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,(p_id_str,recorID))
            connection.commit()
    return True

def deleteRecord(recordID):
    sql = "DELETE FROM `record` WHERE `recordID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,recordID)
        connection.commit()
    return True
#display all record
def showRecord():
    sql = "SELECT * FROM record"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()
    print(result)
    return result
#=======================================================================

def get_current_time():
    taipei = pytz.timezone('Asia/Taipei')
    return datetime.strftime(datetime.now(taipei), "%Y-%m-%d")


def modify_record(data1):
    data = data1
    print(data)
    recordId = data['recordID']
    participants = []
    for i in range(int(data['counter'])):
        p = data.get('participant' + str(i))
        if  p != None and p != '':
            participants.append(data['participant' + str(i)])
    print(participants)
    result = updateRecord(recordId,data['title'],participants)
    return result

def delete_record(data):
    print(data)
    recordID = data['recordID']
    deleteRecord(recordID)
    print("delete", recordID)

def filter_classroom(data1): #開始日期 startDate,開始節數 startSection,結束日期endDate ,結束節數endSection,大樓(building),可容納人數(capacity)
    data = data1
    sql = "SELECT * FROM Classroom"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        classroom_total = cursor.fetchall()
    classroom_total = pd.DataFrame(classroom_total)
    if data['building'] != None:
        building = re.findall("[A-Z]+",data['building'])
        if(len(building) > 0):
            building = building[0]
        else:
            building = ""
        classroom_total = classroom_total.loc[classroom_total["building"] ==  building ]
    if data['capacity'] != None:
        classroom_total = classroom_total.loc[classroom_total["capacity"] > int(data["capacity"]) ]
    print(classroom_total)
    sql = "SELECT * FROM Record"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        record_total = cursor.fetchall()

    record_CR_ID = []
    for r in record_total:
        if r["CR_ID"] in classroom_total["CR_ID"]:
            record_CR_ID.append(r)
    d_startTime = datetime.fromisoformat(str(data["startDate"]))
    d_endTime = datetime.fromisoformat(str(data["endDate"]))
    print("where")
    for r in record_CR_ID:
        startTime = datetime.fromisoformat(str(r["startDate"]))
        endTime = datetime.fromisoformat(str(r["endDate"]))
        after_record = (endTime < d_startTime or (endTime == d_startTime and int(r["endSection"]) < int(data["startSection"])))
        before_record = (startTime > d_endTime or (startTime == d_endTime and int(r["startSection"]) > int(data["endSection"])))
        if not (after_record or before_record):
            classroom_total = classroom_total.drop(classroom_total.loc[classroom_total["CR_ID"] == r["CR_ID"]].index)
    print("here")
    classroom_total = classroom_total.drop("CR_ID",axis = 1)
    classroom_total = classroom_total.T.to_dict().values() 
    print(classroom_total)
    return classroom_total

def borrow(data, borrow_type):
    participants = []
    print("987")
    for i in range(int(data['counter'])):
        p = data.get('participant' + str(i))
        if  p != None and p != '':
            participants.append(data['participant' + str(i)])
    print("123")
    insertRecord(title = data['title'], roomname  = data['roomName'], \
    startDate = data['startDate'], startSection  = data['startSection'], \
    endDate = data['endDate'], endSection  = data['endSection'], participant = participants, \
    bookName = "alien",type = 1)

    return True