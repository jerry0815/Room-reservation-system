import flask
from flask import Flask, request , render_template , redirect , url_for, make_response
import os
import re
import pymysql
import pymysql.cursors
import requests
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from fun import *

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
    insertUser(userName = data['userName'], nickName = "", password = data['password'], email = data['email'], identity = '0' , banned = '0')
    return True

#login and return user information. return status,result
#status:
# 0:success 1:wrong email 2:wrong passward
def validateLogin(email , password):
    sql = "SELECT * FROM users WHERE `email`=%s"
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
        return (0,result)

#for cookie
def loginCheck(email,password):
    sql = "SELECT password FROM users WHERE `email`=%s"
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
        if int(capacity) > 0 and capacity != "":
            sql = "SELECT * FROM classroom WHERE `roomname` = %s AND `capacity` > %s"
            condition = (roomname,capacity)
        else:
            sql = "SELECT * FROM classroom WHERE `roomname` = %s"
            condition = roomname
    else:
        if int(capacity) > 0 and capacity != "":
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
                    item = {"building" : i["building"] , "capacity" : i["capacity"] , "roomName" : i["roomname"] , "status" : item}
                    output.append(item)          
    return output

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
    sql = "SELECT `userName`  FROM `users` WHERE `userID`= %s"
    for result in results:
        p_name = []
        participants = result['participant']
        participants = participants.split(',')
        for i in participants:
            connection.ping(reconnect = True)
            with connection.cursor() as cursor:
                cursor.execute(sql,i)
                tmp = cursor.fetchone()
                if tmp != None:
                    p_name.append(tmp['userName'])
                else :
                    print(i)
        result['participant'] = p_name
    return results

#get the record by id
def getRecordById(id):
    sql = "SELECT * FROM record WHERE `recordID` = %s"
    connection.ping(reconnect = True)
    with connection.cursor() as cursor:
        cursor.execute(sql,id)
        result = cursor.fetchone()
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
    result = getRecordByBooker('jerry')
    print(result)
    return render_template("testDB_record.html" , data = result)
    #return result

#==============================================================================
#calendar part
def insertEvent(service , title , roomname , startDate , startSection , endDate , endSection , participants):
    startTime = datetime.datetime.fromisoformat(startDate)
    endTime = datetime.datetime.fromisoformat(endDate)
    startHours = datetime.timedelta(hours= startSection + 7)
    endHours = datetime.timedelta(hours= endSection + 8)
    startTime = startTime + startHours
    endTime = endTime + endHours
    event = {
    'summary': title,
    'location': ('NTUST ' + roomname) ,
    'description': 'An event from room reservation',
    'start': {
        'dateTime': startTime.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': 'Asia/Taipei',
    },
    'end': {
        'dateTime': endTime.strftime("%Y-%m-%dT%H:%M:%S"),
        'timeZone': 'Asia/Taipei',
    },
    'attendees': [
        {'email': 'linjerry890815@gmail.com'} 
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    event_result = service.events().insert(calendarId='primary', body=event , sendUpdates = True).execute()
    print("created event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])
    return event_result['id']

def updateEvent(service , startDate , startSection , title = "" , participants = None):
    startTime = datetime.datetime.fromisoformat(startDate)
    startHours = datetime.timedelta(hours = startSection + 7)
    startTime = startTime + startHours
    events_result = service.events().list(calendarId="primary", timeMin= startTime.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        id = event['id']
        print(start, event['summary'],id)
    event = events[0]
    attendees = []
    for i in event['attendees']:
        attendees.append(i['email'])
    attendees = attendees + participants
    if title == "":
        title = event['summary']
    print(title)
    new_event = {
    'summary': title,
    'location': event['location'] ,
    'description': 'An event from room reservation',
    'start': {
        'dateTime': event['start']['dateTime'],
        'timeZone': 'Asia/Taipei',
    },
    'end': {
        'dateTime': event['end']['dateTime'],
        'timeZone': 'Asia/Taipei',
    },
    'attendees': [
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    for i in attendees:
        new_event['attendees'].append({'email' : i })
    service.events().update(calendarId = 'primary' , eventId = event['id'] , body = new_event , sendUpdates = True).execute()
    return new_event

def deleteEvent(service , startDate , startSection):
    startTime = datetime.datetime.fromisoformat(startDate)
    startHours = datetime.timedelta(hours = startSection + 7)
    startTime = startTime + startHours
    events_result = service.events().list(calendarId="primary", timeMin= startTime.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    event = events[0]
    print(event)
    service.events().delete(calendarId = 'primary' , eventId = event['id'] , sendUpdates = True).execute()

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "credentials.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/calendar' , 'https://www.googleapis.com/auth/calendar.events']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'
# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See https://flask.palletsprojects.com/quickstart/#sessions.
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    cred = flask.session['credentials']
    if cred['refresh_token']:
        print("I right")
        return flask.redirect('authorize')
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    result = insertEvent(service=service , title = "test insert calendar" , roomname = "TR-313",startDate = "2021-01-20" , startSection=5 , endDate = "2021-01-20" , endSection=8,participants=["linjerry890815@gmail.com"])
    print("insert result eventID: " + result)
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId="primary", timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        return 'No upcoming events found.'
    tmp = "123"
    event = events[0]
    start = event['start'].get('dateTime', event['start'].get('date'))
    tmp = start + " " + event['summary']
    return tmp

    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))

#calendar part
#===============================================================================

"""
if __name__ == '__main__':
    app.debug = True
    app.run() #啟動伺服器
"""


#================================================================
#new

buildings=['研揚大樓(TR)','第四教學大樓(T4)','綜合研究大樓(RB)','國際大樓(IB)','電資館(EE)']

record_ex = {'recordId':'123', 'title':'上課','start_date':'2021-01-30', 'start_section':1, 'end_date':'2021-01-30', 'end_section':10,
'roomName':'TR313', 'building':'研揚大樓(TR)', 'participant':['茶是一種蔬菜湯','茶葉蛋',
'神棍局局長']}

record_ex2 = {'recordId':'456', 'title':'創業', 'start_date':'2021-02-01', 'start_section':1, 'end_date':'2021-01-31', 'end_section':10,
'roomName':'TR411', 'building':'研揚大樓(TR)', 'participant':['勞工',
'CEO','CTO','PM']}

records = [record_ex, record_ex2]

search_ex = {'building':'研揚大樓','roomName':'TR313','capacity':20,
'status':{1:(1,'電機系上課','咕你媽逼'), 10:(0, '投影機故障', 'admin')}}

search_ex2 = {'building':'研揚大樓','roomName':'TR414','capacity':30,
'status':{5:(1,'開會','Jerry'), 14:(0, '椅子壞掉', 'admin')}}

search_result = [search_ex, search_ex2]

def cookie_check():
    """
    check cookie's correctness
    """
    email = request.cookies.get("email")
    password = request.cookies.get('password')
    if loginCheck(email,password):
        return True
    return False

@app.route('/logout')
def logout():
    res = make_response(redirect(url_for("login_page")))
    res.set_cookie(key='email', value='', expires=0)
    res.set_cookie(key='password', value='', expires=0)
    return res


    return redirect(url_for('logout'))

@app.route('/register',methods=['POST','GET'])
def register_page():
    if cookie_check():
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        print('yes123')
        result = request.form
        print(result)
        if register(result):
            #註冊成功
            print("success")
            return redirect(url_for('login_page'))
        else:
            #註冊失敗
            print("error")
            return render_template("register.html")
    return render_template("register.html")

@app.route('/login',methods=['POST','GET'])
def login_page():
    if cookie_check():
        return redirect(url_for('main_page'))
    return render_template("login.html")

@app.route('/search',methods=['POST','GET'])
def search_page():
    if not cookie_check():
        return redirect(url_for('login_page'))
    if request.method =='POST':
        result = request.form
        building = re.findall("[A-Z]+",result['building'])[0]
        print(building)
        search_result = searchClassroom(building = building , capacity = result['capacity'] , roomname = result['roomName'] , date = result['date'])
        print("===")
        print(search_result)
        print("===")
        return render_template("search.html", buildings=buildings, date=result['date'], result=search_result)
    print("template")
    print(buildings)
    return render_template("search.html", buildings=buildings, date=get_current_time(), result=None)
    
@app.route('/borrow',methods=['POST','GET'])
def borrow_page():
    if not cookie_check():
        return redirect(url_for('login_page'))
    return render_template("borrow.html")

@app.route('/record',methods=['POST','GET'])
def record_page():
    if not cookie_check():
        return redirect(url_for('login_page'))

    return render_template("record.html", records=records)

@app.route('/single_record',methods=['POST'])
def single_record_page():
    if not cookie_check():
        return redirect(url_for('login_page'))
    if request.method =='POST':
        return render_template("single_record.html",record=get_record(request.form['id']))
    
    return render_template("single_record.html")

@app.route('/', methods=['POST', 'GET'])
def main_page():
    #if cookie exists and user information is correct, then enter main page 
    if cookie_check():
        return render_template("main.html", user_name = request.cookies.get('email'))


    if request.method =='POST':
        #TODO encryption
        status , result = validateLogin(request.form['email'], request.form['password'])
        if status == 0:
            resp = make_response(render_template("main.html"))
            #set cookie
            resp.set_cookie('email', request.form['email']) #TODO set age
            resp.set_cookie('password', request.form['password']) #TODO set age
            return resp
        #login fail
        else:
            return redirect(url_for('login_page'))
    else:
        return redirect(url_for('login_page'))
         
    
if __name__ == '__main__':
    app.debug = True
    app.secret_key = "test Key"
    app.run()