import flask
from flask import Flask, request , render_template
from flask import redirect , url_for, make_response
import os
import re
import pymysql
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import pytz
from user import *
from record import *
from classroom import *
import datetime

app = Flask(__name__)

dummy_record = {'recordID':'1', 'title':'dummy', 'startDate':'2021-02-01', 'startSection':1, 'endDate':'2021-01-31', 'endSection':10,
'roomName':'TR-411', 'building':'研揚大樓(TR)', 'participant':[]}

#test DB route
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
        {'email': 'chubihaha000@gmail.com'} 
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    event_result = service.events().insert(calendarId='primary', body=event , sendUpdates = "all").execute()
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
    service.events().update(calendarId = 'primary' , eventId = event['id'] , body = new_event , sendUpdates = "all").execute()
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
    service.events().delete(calendarId = 'primary' , eventId = event['id'] , sendUpdates = "all").execute()

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
app.secret_key = "My key"
@app.route('/test')
def test_api_request():
    """
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')
    """
    cred = flask.session['credentials']
    """
    if cred['refresh_token']:
        print("I right")
        return flask.redirect('authorize')
    """
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)

    result = insertEvent(service=service , title = "test insert calendar" , roomname = "TR-313",startDate = "2021-02-20" , startSection=5 , endDate = "2021-02-20" , endSection=8,participants=["linjerry890815@gmail.com"])
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
 
def calendar_process(data , calendar_type):
    """
    if 'credentials' not in flask.session:
        return redirect(url_for('authorize' , data = request.args.get('data') , calendar_type = request.args.get('calendar_type')))
    """
    cred = flask.session['credentials']
    """
    if cred['refresh_token']:
        return redirect(url_for('authorize' , data = request.args.get('data') , calendar_type = request.args.get('calendar_type')))
    """
    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])
    service = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    #insert
    if calendar_type == 0:
        print("insert calendar")
        attend = []
        for i in range(int(data['counter'])):
            p = data.get('participant' + str(i))
            if  p != None and p != '':
                attend.append(data['participant' + str(i)])
        attend = getUserMail(attend)
        print(attend)
        try:
            result = insertEvent(service=service , title = data['title'], roomname  = data['roomName'],\
            startDate = data['startDate'], startSection  = data['startSection'],\
            endDate = data['endDate'], endSection  = data['endSection'],\
            participants = attend)
        except:
            flask.session.pop('credentials')
            print("insert error")
        return 
    #update
    elif calendar_type == 1:
        attend = []
        for i in range(int(data['counter'])):
            p = data.get('participant' + str(i))
            if  p != None and p != '':
                attend.append(data['participant' + str(i)])
        attend = getUserMail(attend)
        try:
            result = updateEvent(service=service , startDate = data['startDate'], startSection  = data['startSection'],\
            title = data['title'], participants = attend)
        except:
            flask.session.pop('credentials')
            print("update error")
    #delete
    elif calendar_type == 2:
        try:
            result = deleteEvent(service=service , startDate = data['startDate'], startSection  = data['startSection'])
        except:
            flask.session.pop('credentials')
            print("delete error")

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = url_for('oauth2callback', _external=True)

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

    return redirect(url_for('main_page'))
    #return flask.redirect(url_for('calendar_process' , data = request.args.get('data') , calendar_type = request.args.get('calendar_type')))

#calendar part
#===============================================================================

#================================================================
#new
buildings=['研揚大樓(TR)','第四教學大樓(T4)','綜合研究大樓(RB)','國際大樓(IB)','電資館(EE)']

weekdays= ['一', '二', '三', '四','五','六','日']

def cookie_check():
    """
    check cookie's correctness
    """
    email = request.cookies.get("email")
    password = request.cookies.get('password')
    return loginCheck(email, password)

def get_current_time():
    taipei = pytz.timezone('Asia/Taipei')
    return datetime.datetime.strftime(datetime.datetime.now(taipei), "%Y-%m-%d")
@app.route('/logout')
def logout():
    res = make_response(redirect(url_for("login_page")))
    res.set_cookie(key='email', value='', expires=0)
    res.set_cookie(key='password', value='', expires=0)
    res.set_cookie(key='userName', value='', expires=0)
    return res

@app.route('/register',methods=['POST','GET'])
def register_page():
    if cookie_check()[0]:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        result = request.form
        if register(result):
            #註冊成功
            return render_template("register.html", message="register_success")
        else:
            #註冊失敗
            return render_template("register.html", message="register_error")
    return render_template("register.html")

@app.route('/login',methods=['POST','GET'])
def login_page():
    if cookie_check()[0]:
        return redirect(url_for('main_page'))
    if request.method =='POST':
        #TODO encryption
        email = request.form['email'] + "@gmail.com";
        login_status = validateLogin(email, request.form['password'])
        #login fail
        if login_status[0]:
            if login_status[0] == 1: #email error
                return render_template("login.html", message="email_error")
            elif login_status[0] == 2: #password error
                return render_template("login.html", message="password_error")
        #login success
        else:
            resp = make_response(redirect('authorize'))
            #resp = make_response(render_template("main.html", admin=loginCheck(email, request.form['password'])[1]))
            #set cookie
            resp.set_cookie('email', email) 
            resp.set_cookie('password', request.form['password'])
            resp.set_cookie('userName', login_status[1])
            return resp
    return render_template("login.html", message=None)

@app.route('/search',methods=['POST','GET'])
def search_page():
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))
    if request.method =='POST':
        result = request.form
        building = re.findall("[A-Z]+",result['building'])
        if(len(building) > 0):
            building = building[0]
        else:
            building = ""
        search_result = searchClassroom(building = building , capacity = result['capacity'] , roomname = result['roomName'] , date = result['date'])
        return render_template("search.html", buildings=buildings, date=result['date'], result=search_result, admin = check[1] )
    return render_template("search.html", buildings=buildings, date=get_current_time(), result=None, admin = check[1] )
    
@app.route('/borrow',methods=['POST','GET'])
def borrow_page():
    message = ""
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))

    userData = getUser(request.cookies.get('userName'))
    #The user is banned:
    if userData[1]['banned']:
        return render_template("borrow.html", buildings=buildings, admin=check[1], message="ban")

    allUserNames = getAllUserName()
    allUserNames.remove(request.cookies.get('userName'))

    if request.method == "POST":
            #To do borrow()
        result = borrow(request.form, request.form['borrow_type'] , request.cookies.get("userName"))
        if request.form['borrow_type'] == "borrow":
            if result: 
                message="borrow_success"
                calendar_process(request.form , 0)
            else:
                message="borrow_fail"
        elif request.form['borrow_type'] == "ban":
            if result: 
                message="ban_success"
            else:
                message="ban_fail"
        
        return render_template("borrow.html", buildings=buildings, admin=check[1], message=message, allUserNames=allUserNames)
      
    
    return render_template("borrow.html", buildings=buildings, admin=check[1], allUserNames=allUserNames)

@app.route('/borrow_search',methods=['POST','GET'])
def borrow_search_page():
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))

    if request.method == "POST":
        print('borrow_search:',request.form)
        #to to search for boroow
        result = filter_classroom(request.form)
        return render_template("borrow_search.html", result=result)

    return render_template("borrow_search.html")

@app.route('/record',methods=['POST','GET'])
def record_page():
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))
    records = []
    email = request.cookies.get("email")
    if email != None:
        records = getRecordByBookerEmail(email)
    for i in records:
        print(i['title'] , i['participant'])
    return render_template("record.html", userName = request.cookies['userName'], records=records, admin = check[1])

@app.route('/single_record',methods=['POST'])
def single_record_page():
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))

    if request.method =='POST':
        if request.form['postType'] == 'get':
            allUserNames = getAllUserName()
            allUserNames.remove(request.cookies.get('userName'))
            record = getRecordById(request.form['recordID'])
            remainingUserNames = []
            for name in allUserNames:
                if name not in record['participant']:
                    remainingUserNames.append(name)
            return render_template("single_record.html",record = record, admin = check[1], remainingUserNames = remainingUserNames)
        elif request.form['postType'] == 'modify':
            modify_record(request.form)
            return render_template("single_record.html",record = dummy_record, admin = check[1], message="modify_success")
        elif request.form['postType'] == 'delete':
            deleteRecord(request.form['recordID'])
            return redirect(url_for('record_page'))
    return redirect(url_for('main_page'))

@app.route('/', methods=['POST', 'GET'])
def main_page():
    check = cookie_check()
    #if cookie exists and user information is correct, then enter main page 
    if check[0]:
        return render_template("main.html", user_name = request.cookies.get('email'), admin=check[1])
    return redirect(url_for('login_page'))
         
@app.route('/account_management', methods=['POST', 'GET'])
def account_management_page():
    #if cookie exists and user information is correct, then enter main page 
    check = cookie_check()
    message = ""
    if check[0] and check[1] == "admin":
        allUserNames = getAllUserName()
        allUserNames.remove(request.cookies.get('userName'))
        if request.method == "POST":

            #do operation
            if request.form['postType'] == "search":
                result = getUser(request.form['userName'])
                if not result[0]:
                    message = "error"
                return render_template("account_management.html", user = result[1], admin=check[1], message = message, allUserNames = allUserNames)
            elif request.form['postType'] == "delete":
                result = deleteAccount(request.form['userID'])
            elif request.form['postType'] == "ban":
                result = banAccount(request.form['userID'])
            elif request.form['postType'] == "unban":
                result = unBanAccount(request.form['userID'])

            #check operation result
            if result:
                result = request.form['postType'] + '_success'
            else:
                result = request.form['postType'] + '_fail'
            return render_template("account_management.html", user = None, admin=check[1], message = result, allUserNames = allUserNames)
        return render_template("account_management.html", user = None, admin=check[1], allUserNames = allUserNames)
    else:
        return redirect(url_for('login_page'))
      
@app.route('/search_single',methods=['POST','GET'])
def search_single_page():
    check = cookie_check()
    if not check[0]:
        return redirect(url_for('login_page'))
    if request.method =='POST':
        classroom_data = searchOneClassroom(CR_ID = request.form['CR_ID'] , date = request.form['start_date'])
        start_date = request.form['start_date']
        start_date = datetime.datetime(int(start_date.split('-')[0]), 
                                        int(start_date.split('-')[1]),
                                        int(start_date.split('-')[2]))
        dates = [start_date]
        dates_weekdays = []
        for i in range(1,7):
            dates.append(start_date + datetime.timedelta(i))
        for i in range(7):
            dates_weekdays.append(weekdays[dates[i].weekday()])
            dates[i] = datetime.datetime.strftime(dates[i], "%Y-%m-%d")
            
        print(dates, dates_weekdays)
        return render_template("search_single.html",classroom = classroom_data,
                                                    dates = dates,
                                                    dates_weekdays = dates_weekdays,
                                                    admin = check[1])
    return redirect(url_for('main_page'))


if __name__ == '__main__':
    app.debug = True
    app.secret_key = "test Key"
    app.run()