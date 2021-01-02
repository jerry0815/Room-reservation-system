from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



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
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials_local.json', SCOPES)
            creds = flow.run_console()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

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
    event_result = service.events().insert(calendarId='primary', body=event , sendUpdates = 'all').execute()
    print("created event")
    print("id: ", event_result['id'])
    print("summary: ", event_result['summary'])
    print("starts at: ", event_result['start']['dateTime'])
    print("ends at: ", event_result['end']['dateTime'])
    return event_result['id']

#how to choose which information change?

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
    #print(attendees)
    #print(event)
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
    service.events().update(calendarId = 'primary' , eventId = event['id'] , body = new_event , sendUpdates = 'all').execute()
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
    service.events().delete(calendarId = 'primary' , eventId = event['id'] , sendUpdates = 'all').execute()

def main():
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

    #result = updateEvent(service  = service , startDate = '2021-01-20' , startSection = 4 , title = 'update calendar test' , participants = ['b10730002@gapps.ntust.edu.tw'])
    #print(result)
    result = insertEvent(service=service , title = "test insert calendar" , roomname = "TR-313",startDate = "2021-02-20" , startSection=5 , endDate = "2021-02-20" , endSection=8,participants=["linjerry890815@gmail.com"])
    # Call the Calendar API
    startTime = datetime.datetime.fromisoformat("2021-01-07")
    startHours = datetime.timedelta(hours= 19)
    startTime = startTime + startHours
    print('Getting the upcoming 10 events')
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print(startTime)
    events_result = service.events().list(calendarId="primary", timeMin= startTime.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    id_list = []
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        id = event['id']
        print(start, event['summary'],id)
        id_list.append(id)

    deleteEvent(service  = service , startDate = '2021-01-20' , startSection = 4)
    """
    event = {
    'summary': 'Google calendar my test',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2021-01-10T09:00:00-07:00',
        'timeZone': 'Asia/Taipei',
    },
    'end': {
        'dateTime': '2021-01-10T09:00:00-07:00',
        'timeZone': 'Asia/Taipei',
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        {'email': 'jerrylulala@gmail.com'}
        {'email': 'lpage@example.com'},
        {'email': 'sbrin@example.com'},
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    


    calendar_list = service.calendarList().list().execute()
    print(len(calendar_list))
    for i in calendar_list["items"]:
        print(i["id"])
    #print(calendar_list["items"][0]['id'])
    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    
    events_result = service.events().list(calendarId="primary", timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    """

if __name__ == '__main__':
    main()