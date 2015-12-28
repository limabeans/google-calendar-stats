from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

def get_upcoming_10_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'



def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_cal_ids(service):
    calendar_ids = {}
    page_token = None
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        # print(calendar_list)
        for c in calendar_list['items']:
            name = c['summary']
            c_id = c['id']
            calendar_ids[name] = c_id
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break
    return calendar_ids

def get_events_list(service, cal_id):
    events_lst = []
    page_token = None
    while True:
        events = service.events().list(calendarId=cal_id, pageToken=page_token).execute()
        events_lst += events
        for event in events['items']:
            print(event['summary'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return events_lst


def get_weeks_stats(service, cal_id):
    secs = 0
    events_lst = []
    page_token = None
    tmp = datetime.datetime(month=1, day=18, year=2016)
    start_day = datetime.datetime(month=1, day=18, year=2016).isoformat()+'Z'
    end_day = (tmp + datetime.timedelta(days=7)).isoformat()+'Z'

    while True:
        events = service.events().list(calendarId=cal_id, pageToken=page_token, timeMin=start_day, timeMax=end_day).execute()
        events_lst += events
        for event in events['items']:
            s = event['start']['dateTime']
            e = event['end']['dateTime']
            s_d = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S-08:00')
            e_d = datetime.datetime.strptime(e, '%Y-%m-%dT%H:%M:%S-08:00')
            secs += (e_d - s_d).total_seconds()
            print(event['summary'], s, e)
            
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    print(secs/3600)
    return events_lst

    
    


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar_ids = get_cal_ids(service)
    # print (get_events_list(service, calendar_ids['life']))
    # print(calendar_ids['class'])
    print('first weeks classes:')
    get_weeks_stats(service, calendar_ids['class'])
    # get_upcoming_10_events(service)
if __name__ == '__main__':
    main()






