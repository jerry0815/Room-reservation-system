from flask import Flask, request , render_template , redirect , url_for
import os
import pymysql
import pymysql.cursors

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

app = Flask(__name__)

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
def insertUser(userName = "jerry", nickName = "", password = "123456798", email = "jerry@gmail.com", identity = '0' , banned = '0'):
    if nickName == "":
        nickName = userName
    sql = "INSERT INTO `users` (`userName`, `nickName`,`password` , `email` , `identity` , `banned`) VALUES (%s,%s,%s,%s,%s,%s)"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,(userName , nickName , password , email,identity , banned))
        connection.commit()

#login and return user information. return status,result
#status:
# 0:success 1:wrong email 2:wrong passward
def validateLogin(email , password):
    sql = "SELECT * FROM users WHERE `email`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        result = cursor.fetchone()
    #wrong email
    if result == None:
        return (1 , None)
    #wrong passward
    if result["password"] != password:
        return (2,None)
    else:
        return (0,result)

#for cookie
def loginCheck(email,passward):
    sql = "SELECT passward FROM users WHERE `email`=%s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,email)
        result = cursor.fetchone()
    #wrong email
    if result == None:
        return 1
    #wrong passward
    if result["password"] != password:
        return 2
    else:
        return 0


#modify user's nickname 
def modifyNickName(userName , nickName):
    sql = " UPDATE users SET nickName = %s WHERE userName = %s "
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql , (nickName,userName))
        connection.commit()

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
    print(result)
    return result

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
def insertRecord(title = "testing record", roomname  = "TR-306", startDate = "2020-12-30", startSection  = "5", endDate = "2020-12-30", endSection  = "8", participant = ['jerry','alien','wacky'], bookName = "jerry",type = "0"):

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
def searchClassroom(building = "" , capacity = -1 , roomname = "" , date = "2020-01-01"):
    if roomname != "":
        if  building != "":
            if roomname[0:2] != building:
                return None
        if capacity > 0 :
            sql = "SELECT * FROM classroom WHERE `roomname` = %s AND `capacity` > %s"
            condition = (roomname,capacity)
        else:
            sql = "SELECT * FROM classroom WHERE `roomname` = %s"
            condition = roomname
    else:
        if capacity > 0 :
            if building != "":
                sql = "SELECT * FROM classroom WHERE `building` = %s AND `capacity` > %s"
                condition = (building,capacity)
            else:
                sql = "SELECT * FROM classroom WHERE `capacity` = %s"
                condition = capacity
        elif building != "":
            sql = "SELECT * FROM classroom WHERE `building` = %s"
            condition = building
        else:
            print("no condition")
    
    with connection.cursor() as cursor:
        cursor.execute(sql,condition)
        result = cursor.fetchall()
    print(result)
    print("==========================")
    output = []
    sql = "SELECT * FROM record WHERE `CR_ID` = %s AND `startDate` = %s"
    for i in result:
        with connection.cursor() as cursor:
            cursor.execute(sql,(i["CR_ID"],date))
            tmp = cursor.fetchall()
            if tmp != ():
                for j in tmp:
                    item = processRecord(j)
                    #building , capacity , roomname , status
                    item = (i["building"] , i["capacity"] , i["roomname"] , item)
                    output.append(item)          
    print(output)
    return result

#search for one classroom and return records of a week
# return format:  list[ building , capacity , roomname , dict{id : tuple()}(7days) ]
#parameter (classroom name , date of the week)
def searchOneClassroom(roomname = "" , date = "2020-12-29") :
    sql = "SELECT * FROM classroom WHERE `roomname` = %s"
    with connection.cursor() as cursor:
        cursor.execute(sql,roomname)
        result = cursor.fetchone()
    building = result["building"]
    capacity = result["capacity"]
    CR_ID = result["CR_ID"]
    today = datetime.datetime.fromisoformat(date)
    n = today.weekday()
    delta = datetime.timedelta(days = n)
    startDay = str((today - delta).date())
    delta = datetime.timedelta(days = 6 - n)
    endDay = str((today + delta).date())
    print(startDay + " ~ " + endDay)
    sql = "SELECT * FROM record WHERE `CR_ID` = %s AND `startDate` >= %s AND `endDate` <= %s"
    output = []
    with connection.cursor() as cursor:
        cursor.execute(sql,(CR_ID,startDay,endDay))
        tmp = cursor.fetchall()
        if tmp != ():
            for d in range(0,6):
                delta = datetime.timedelta(days = n - d)
                dailyItem = {}
                for j in tmp:
                    item = processRecord(j,str((today - delta).date()))
                    if item != None:
                        dailyItem.update(item)
                output.append(dailyItem)  
            return [building , capacity , roomname , output]


#
#def getRecord(startDate , startSection , endDate, endSection , roomname):

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
        result = cursor.fetchall()
    return result


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

"""
with connection.cursor() as cursor:
    # Create a new record
    sql = "INSERT INTO `Account` (`email`, `password` , `name`) VALUES (%s, %s , %s)"
    cursor.execute(sql, ('alien@gmail.com', 'QQQQQQ' , 'Alien'))

connection.commit()
"""

#insertRecord()


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

@app.route('/testDB_classroom',methods=['POST','GET'])
def testDB_classroom():
    result = showClassroom()
    return render_template("testDB_classroom.html" , data = result)
    #return result

@app.route('/testDB_users',methods=['POST','GET'])
def testDB_users():
    result = validateLogin("jerry","123456789")
    if result == None:
        return render_template("testDB_users.html" , data = result , status = 1)
    return render_template("testDB_users.html" , data = result , status = 0)
    #return result

@app.route('/testDB_record',methods=['POST','GET'])
def testDB_record():
    result = showRecord()
    return render_template("testDB_record.html" , data = result)
    #return result

@app.route('/google390a5a29c97e707c.html')
def google390a5a29c97e707c():
    return "google-site-verification: google390a5a29c97e707c.html"


def get_calendar_service():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    """
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    """
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

@app.route('/calendar')
def calendar():
    service = get_calendar_service()
    # Call the Calendar API
    print('Getting list of calendars')
    calendars_result = service.calendarList().list().execute()

    calendars = calendars_result.get('items', [])

    if not calendars:
        print('No calendars found.')
    for calendar in calendars:
        summary = calendar['summary']
        id = calendar['id']
        primary = "Primary" if calendar.get('primary') else ""
        print("%s\t%s\t%s" % (summary, id, primary))
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    
    events_result = service.events().list(calendarId="primary", timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    tmp = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        tmp.append([start + " " + event['summary']])
        print(start, event['summary'])
    return tmp
if __name__ == '__main__':
    app.debug = True
    app.run() #啟動伺服器