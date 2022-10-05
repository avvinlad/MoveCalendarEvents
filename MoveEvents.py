import os.path
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json. !!!
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Process
    try:
        service = build('calendar', 'v3', credentials=creds)

        page_token_calendars = None
        # Holds all calendars that are not excluded
        calendars = []
        # holds all events for all calendars
        allEvents = []
        # If you want to exclude any calendars from the list to change,
        # add the ID of the calendar to the list
        EXCLUSIONS = ["INSERT CALENDAR IDs OF CALENDARS YOU WANT TO EXCLUDE"]
        # ID of calendar you want to move events to (destination of moved events)
        TARGET_CALENDAR_ID = "INSERT TARGET CALENDAR ID HERE"
        # Starting time to target the events (Currently this is set to JAN 1st, 2021)
        # This means it will only gather events from 01/01/2021 - PRESENT
        TIME_MIN = "2021-01-01T10:00:00-07:00"



        # Loop through calendars
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token_calendars).execute()
            for calendar_list_entry in calendar_list['items']:
                if (calendar_list_entry['id'] not in EXCLUSIONS):
                    # Add to calendars list
                    calendars.append({"id": calendar_list_entry['id'], "name": calendar_list_entry['summary']})
                    
                    # Loop through events
                    page_token_events = None
                    while True:
                        # Get list of events, loop and append each to allEvents
                        events = service.events().list(calendarId=calendar_list_entry['id'], pageToken=page_token_events, timeMin=TIME_MIN).execute()
                        for event in events['items']:
                            allEvents.append({"calendarID": event['organizer']['email'], "eventID": event['id'], "eventName": event['summary'], "calendarName": event['organizer']['displayName']})
                        
                        # Get next page of events 
                        page_token_events = events.get('nextPageToken')
                        if not page_token_events:
                            break

            # Get next page of calendars
            page_token_calendars = calendar_list.get('nextPageToken')
            if not page_token_calendars:
                break
        
        # UPDATE THE CALENDARS
        try: 
            print('Choose:')
            print('(1) Print Calendars Of Events To Move')
            print('(2) Show All Events Being Changed')
            print('(3) Move Events')
            choice = int(input('Enter: '))

            if (choice == 1):
                print('Calendars To Move')
                for cal in calendars:
                    print(cal['id'])
            elif (choice == 2):
                print('Show All Events To Change')
                print('# of Events: {}'.format(len(allEvents)))
                for event in allEvents:
                    print('{} -> {}'.format(event['calendarName'], event['eventName']))
            elif (choice == 3):
                for event in allEvents:
                    service.events().move(
                        calendarId=event['calendarID'],
                        eventId=event['eventID'],
                        destination=TARGET_CALENDAR_ID
                    ).execute()
                print("Move Complete!")
            else:
                print('Invalid Entry...')
            
        except Exception as error:
            print("An error occurs {}".format(error)) 

    except HttpError as error:
        print('An error occurred: {}'.format(error))


if __name__ == '__main__':
    main()