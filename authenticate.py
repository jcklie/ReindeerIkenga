'''
Created on Sep 3, 2012

@author: Jan-Christoph Klie
'''
import httplib2

from oauth2client.client import SignedJwtAssertionCredentials 
from apiclient.discovery import build

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


f = file("key.p12", "rb")
key = f.read()
f.close()

credentials = SignedJwtAssertionCredentials(
                                                service_account_name='423291807109-jivekem4vanfq7r2avl7ctkkv241iefr@developer.gserviceaccount.com',
                                                private_key=key,
                                                
                                                scope='https://www.googleapis.com/auth/calendar'                                            
                                            )

http = httplib2.Http()
http = credentials.authorize(http)

service = build('calendar', 'v3', http=http)
request = service.events().insert(calendarId='9jehd9lrvaqpotvghihlpmj9t0@group.calendar.google.com', body=event)

response = request.execute()

print(response)