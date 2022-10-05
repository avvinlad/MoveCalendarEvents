import os.path

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
        # add the NAME of the calendar to the list
        EXCLUSIONS = []
        # ID of calendar you want to move events to (destination of moved events)
        TARGET_CALENDAR_ID = ""
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
                            allEvents.append(event)
                        
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
            for event in allEvents:
                service.events().move(
                    calendarId=event['organizer']['email'], eventId=event['id'],
                    destination=TARGET_CALENDAR_ID
                ).execute()
            print("Complete!")
            
        except Exception as error:
            print("An error occurs {}".format(error)) 

    except HttpError as error:
        print('An error occurred: {}'.format(error))


if __name__ == '__main__':
    main()