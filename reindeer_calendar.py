'''
Created on Sep 18, 2012

@author: Jan-Christoph Klie
'''

import urllib2
import datetime
import time
import re
import httplib2
import rfc3339
from bs4 import BeautifulSoup

from apiclient.discovery import build
from oauth2client.client import Credentials

blocks = []
blocks.append(( datetime.date(2012, 9, 3), datetime.date(2012, 11, 23)  ))
blocks.append(( datetime.date(2013, 2, 18), datetime.date(2013, 5, 10)  ))
blocks.append(( datetime.date(2013, 9, 2), datetime.date(2013, 11, 22)  ))
blocks.append(( datetime.date(2014, 2, 17), datetime.date(2014, 5, 9)  ))

URL = 'http://vorlesungsplan.dhbw-mannheim.de/index.php?action=view&gid=3067001&uid=3967001&date={0}'
GRID = re.compile('<div class="ui-grid-e">.*(?=</div>.?</div>.?</body>)', re.DOTALL)
CALENDAR_ID = '9jehd9lrvaqpotvghihlpmj9t0@group.calendar.google.com'

'''
    Helper functions
'''

def __create_datetime(s):
    p = re.split('[ \.:]', s)
    return rfc3339.rfc3339(datetime.datetime(int(p[3]), int(p[2]), int(p[1]), int(p[4]), int(p[5])))

def __timestamps(block):
    d = blocks[block][0]
    de = blocks[block][1]
    while d < de:
        yield int(time.mktime(d.timetuple()))
        d = d + datetime.timedelta(7 - d.weekday())
        
def __create_service():
    with open('credentials', 'rw') as f:
        credentials = Credentials.new_from_json(f.read())

    http = httplib2.Http()
    http = credentials.authorize(http)
    
    return build('calendar', 'v3', http=http)
        
'''
    The magic.
'''
        
def extract(dates):
    data = {}
    now = datetime.datetime.now()
    
    for m in dates:        
        html_doc = urllib2.urlopen(URL.format(m)).read()
        soup = BeautifulSoup(html_doc)
        appointments = []
        html_days = soup.find_all("ul", attrs= { 'data-role' : "listview" } )
        
        for day in html_days:
            
            date = day.find( "li", attrs= { 'data-role' : "list-divider" } ).text
            html_appointments = day.find_all( "li", class_=True )           

            for appointment in html_appointments:
                time = appointment.find( "div", class_='cal-time' ).text
                hours = time.split('-')
                assert len(hours) == 2
                start = __create_datetime('{0}.{1} {2}'.format(date, now.year, hours[0]))
                end  = __create_datetime('{0}.{1} {2}'.format(date, now.year, hours[1]))
                room = appointment.find( "div", class_='cal-res' ).text
                text = appointment.find( "div", class_='cal-title' ).text
                appointments.append( (text, room, start, end) )
            
        data[m] = appointments
    return data

def clear_calendar(block):   
    print('Clear calendar!') 
    service = __create_service()    
    request = service.events().list(calendarId=CALENDAR_ID, timeMin=rfc3339.rfc3339(blocks[block][0]))   
    response = request.execute() 
    if 'items' in response:
        for e in response['items']:
            request = service.events().delete(calendarId=CALENDAR_ID, eventId=e['id'])   
            response = request.execute() 
        clear_calendar(block)
    else:
        return
    
def update_calendar(data):
    service = __create_service()
    
    event = {
         'summary' : '',
         'location' : '',
         'start' : { 'dateTime' : '' },
         'end' :    { 'dateTime' : '' }
    }
    
    for day in data.itervalues():     
        for appointment in day:
            print(appointment)
            event['summary'] = appointment[0]
            event['location'] = appointment[1]
            event['start']['dateTime'] = appointment[2]
            event['end']['dateTime'] = appointment[3]            
            
            request = service.events().insert(calendarId=CALENDAR_ID, body=event)
            print(event)
            print(event['summary'].encode("utf-8")) 
            print(request.execute())

if __name__ == "__main__":
    data = extract( __timestamps(0) )
    clear_calendar(0)
    update_calendar(data)
    