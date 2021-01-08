import pymysql
from connect import connection
from datetime import datetime , timedelta
import re
import pandas as pd
import time

#transform list of id to str O
def listIdToStr(id_list):
    if id_list == None or len(id_list) == 0:
        return ","
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
        connection.commit()
        B_ID = cursor.fetchone()["userID"]

    #get classroom CR_ID
    sql = "SELECT  `CR_ID` FROM `classroom` WHERE `roomname`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,roomname)
        connection.commit()
        CR_ID = cursor.fetchone()["CR_ID"]
    print("CR_ID = "  + str(CR_ID))
    #process participant
    p_id = []
    sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
    for ppl in participant:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,ppl)
            connection.commit()
            result = cursor.fetchone()
            if result != None:
                p_id.append(result["userID"])
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
            connection.commit()
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
            sql = "SELECT * FROM classroom WHERE `roomname` = %s AND `capacity` >= %s"
            condition = (roomname,capacity)
        else:
            sql = "SELECT * FROM classroom WHERE `roomname` = %s"
            condition = roomname
    else:
        if capacity != None and capacity != "" and int(capacity) > 0:
            if building != "":
                sql = "SELECT * FROM classroom WHERE `building` = %s AND `capacity` >= %s"
                condition = (building,capacity)
            else:
                sql = "SELECT * FROM classroom WHERE `capacity` >= %s"
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
        connection.commit()
        result = cursor.fetchall()
    output = []
    sql = "SELECT * FROM record WHERE `CR_ID` = %s AND `startDate` = %s"
    print(result)
    for i in result:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,(i["CR_ID"],date))
            connection.commit()
            tmp = cursor.fetchall()
            if tmp != ():
                for j in tmp:
                    item = processRecord(j , date)
                    #building , capacity , roomname , status
                    item = {"CR_ID" : i["CR_ID"] , "building" : i["building"] , "capacity" : i["capacity"] , "roomName" : i["roomname"] , "status" : item}
                    output.append(item)        
            else:
                item = {"CR_ID" : i["CR_ID"] , "building" : i["building"] , "capacity" : i["capacity"] , "roomName" : i["roomname"] , "status" : {}}
                output.append(item)
    return output

#search for one classroom and return records of a week
# return format:  dict{ 'CR_ID' : CR_ID ,'building' : building , 'capacity' : capacity , 'roomName' : roomname , 'status' : dict{id : tuple()}(7days) }
#parameter (classroom name , date of the week)
def searchOneClassroom(CR_ID = "" , date = "2020-12-29") :
    sql = "SELECT * FROM classroom WHERE `CR_ID` = %s"
    with connection.cursor() as cursor:
        cursor.execute(sql,CR_ID)
        connection.commit()
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
        connection.commit()
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
            return {'CR_ID' : CR_ID , 'building' : building , 'capacity' : capacity , 'roomName' :roomname , 'status' : output}
        else:
            for d in range(0,7):
                output.append({})
            return {'CR_ID' : CR_ID , 'building' : building , 'capacity' : capacity , 'roomName' :roomname , 'status' : output}

#search the records the user book
def getRecordByBooker(userName):
    sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,userName)
        connection.commit()
        B_ID = cursor.fetchone()["userID"]

    sql = "SELECT  * FROM `record` WHERE `B_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,B_ID)
        connection.commit()
        results = cursor.fetchall()
    #sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"
    for result in results:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql2,result['CR_ID'])
            connection.commit()
            tmp = cursor.fetchone()
        result['roomName'] = tmp
        p_name = []
        participants = result['participant']
        participants = participants.split(',')
        if len(participants) == 0:
            continue
        sql1 = "SELECT `userName` FROM `users` WHERE `userID` IN ({seq})".format(seq=','.join(['%s']*len(participants)))
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,participants)
            connection.commit()
            tmp = cursor.fetchall()
        for i in tmp:
            if i != None:
                p_name.append(i['userName'])
        result['participant'] = p_name
    return results

#search the records the user's email book
def getRecordByBookerEmail(email):
    sql = "SELECT  `userID` FROM `users` WHERE `email`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        connection.commit()
        B_ID = cursor.fetchone()["userID"]

    sql = "SELECT  * FROM `record` WHERE `B_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,B_ID)
        connection.commit()
        results = cursor.fetchall()
    #sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"

    for result in results:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql2,result['CR_ID'])
            connection.commit()
            tmp = cursor.fetchone()
        result['roomName'] = tmp['roomname']
        p_name = []
        participants = result['participant']
        participants = participants.split(',')
        if len(participants) == 0:
            continue
        sql1 = "SELECT `userName` FROM `users` WHERE `userID` IN ({seq})".format(seq=','.join(['%s']*len(participants)))
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql1,participants)
            connection.commit()
            tmp = cursor.fetchall()
        for i in tmp:
            if i != None:
                p_name.append(i['userName'])
        result['participant'] = p_name
    return results

#get the record by id
def getRecordById(id):
    sql = "SELECT * FROM `record` WHERE `recordID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,id)
        connection.commit()
        result = cursor.fetchone()
    if result == None:
        print("no id of this result")
        return None
    sql1 = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    sql2 = "SELECT `roomname`  FROM `classroom` WHERE `CR_ID`= %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql2,result['CR_ID'])
        connection.commit()
        tmp = cursor.fetchone()
    result['roomName'] = tmp['roomname']
    p_name = []
    participants = result['participant']
    participants = participants.split(',')
    for i in participants:
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql1,i)
            connection.commit()
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
    if participants != None and len(participants) != 0:
        p_id = []
        """
        sql = "SELECT  `userID` FROM `users` WHERE `userName`= %s FOR UPDATE"
        for ppl in participants:
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                cursor.execute(sql,ppl)
                result = cursor.fetchone()
                if result != None:
                    p_id.append(result["userID"])
        """
        sql = "SELECT `userID` FROM `users` WHERE `userName` IN ({seq})".format(seq=','.join(['%s']*len(participants)))
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,participants)
            connection.commit()
            result = cursor.fetchall()
        for i in result:
            if i != None:
                p_id.append(i["userID"])
        p_id_str = listIdToStr(p_id)
        sql = "UPDATE `record` SET `participant` = %s WHERE `recordID` = %s"
        connection.ping(reconnect = True)
        with connection.cursor() as cursor:
            cursor.execute(sql,(p_id_str,recordID))
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
        connection.commit()
        result = cursor.fetchall()
    print(result)
    return result

def modify_record(data):
    recordId = data['recordID']
    participants = []
    for i in range(int(data['counter'])):
        p = data.get('participant' + str(i))
        if  p != None and p != '':
            participants.append(data['participant' + str(i)])
    print(participants)
    result = updateRecord(recordId,data['title'],participants)
    return result

def borrow(data, borrow_type , booker):
    """
    borrow a classroom
    process data and call insertRecord
    """
    participants = []
    have = 0
    if borrow_type == 'ban':
        borrow_type = 0
    else:
        borrow_type = 1
    sql = "SELECT `CR_ID` FROM `classroom` WHERE `roomname` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,data['roomName'])
        connection.commit()
        CR_ID = cursor.fetchone()['CR_ID']
        
    sql = "SELECT * FROM `record` WHERE `CR_ID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,CR_ID)
        connection.commit()
        record_total = cursor.fetchall()
    d_startTime = datetime.fromisoformat(str(data["startDate"]))
    d_endTime = datetime.fromisoformat(str(data["endDate"]))
    record_delete = []
    for r in record_total:
        startTime = datetime.fromisoformat(str(r["startDate"]))
        endTime = datetime.fromisoformat(str(r["endDate"]))
        after_record = (endTime < d_startTime or (endTime == d_startTime and int(r["endSection"]) < int(data["startSection"])))
        before_record = (startTime > d_endTime or (startTime == d_endTime and int(r["startSection"]) > int(data["endSection"])))
        if not (after_record or before_record):
            record_delete.append(r)
            have = 1
    #already have record
    if borrow_type == 1 and have == 1:
        return False
    if borrow_type == 0:
        for r in record_delete:
            deleteRecord(r['recordID'])
    for i in range(int(data['counter'])):
        p = data.get('participant' + str(i))
        if  p != None and p != '':
            participants.append(data['participant' + str(i)])
    insertRecord(title = data['title'], roomname  = data['roomName'], \
    startDate = data['startDate'], startSection  = data['startSection'], \
    endDate = data['endDate'], endSection  = data['endSection'], participant = participants, \
    bookName = booker,type = borrow_type)

    return True

def filter_classroom(data): #開始日期 startDate,開始節數 startSection,結束日期endDate ,結束節數endSection,大樓(building),可容納人數(capacity)
    """
    get the record that between the time period
    """
    sql = "SELECT * FROM Classroom"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        connection.commit()
        classroom_total = cursor.fetchall()
    classroom_total = pd.DataFrame(classroom_total)
    if data['building'] != None:
        building = re.findall("[A-Z0-9]+",data['building'])
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
        connection.commit()
        record_total = cursor.fetchall()
    record_CR_ID = []
    for r in record_total:
        if r["CR_ID"] in classroom_total["CR_ID"]:
            record_CR_ID.append(r)
    d_startTime = datetime.fromisoformat(str(data["startDate"]))
    d_endTime = datetime.fromisoformat(str(data["endDate"]))
    for r in record_CR_ID:
        startTime = datetime.fromisoformat(str(r["startDate"]))
        endTime = datetime.fromisoformat(str(r["endDate"]))
        after_record = (endTime < d_startTime or (endTime == d_startTime and int(r["endSection"]) < int(data["startSection"])))
        before_record = (startTime > d_endTime or (startTime == d_endTime and int(r["startSection"]) > int(data["endSection"])))
        if not (after_record or before_record):
            classroom_total = classroom_total.drop(classroom_total.loc[classroom_total["CR_ID"] == r["CR_ID"]].index)
    classroom_total = classroom_total.drop("CR_ID",axis = 1)
    classroom_total = classroom_total.T.to_dict().values() 
    return classroom_total

