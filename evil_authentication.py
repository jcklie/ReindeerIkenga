'''
Created on Sep 3, 2012

@author: Jan-Christoph Klie
'''

import httplib2
from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build
from oauth2client.client import Credentials

flow = flow_from_clientsecrets('client_secrets.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='urn:ietf:wg:oauth:2.0:oob')

event = {
         'summary' : 'Appointment',
         'location' : 'Somewhere',
         'start' : {
                    'dateTime' : '2012-09-03T10:00:00.000-07:00'
                    },
         'end' :    {
                 'dateTime' : '2012-09-03T10:25:00.000-07:00'
                    }
}

auth = False
if auth:
    auth_uri = flow.step1_get_authorize_url()
    print(auth_uri)
    code = raw_input()
    credentials = flow.step2_exchange(code)
    print(credentials)
    
    with open('credentials', 'wr') as f:
        f.write(credentials.to_json())
    
    
    print( credentials.to_json() )

with open('credentials', 'rw') as f:
    credentials = Credentials.new_from_json(f.read())

http = httplib2.Http()
http = credentials.authorize(http)

service = build('calendar', 'v3', http=http)
request = service.events().insert(calendarId='9jehd9lrvaqpotvghihlpmj9t0@group.calendar.google.com', body=event)

response = request.execute()

print(response)