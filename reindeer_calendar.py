'''
Created on Sep 3, 2012

@author: Jan-Christoph Klie
'''
import urllib2
import datetime
import time
import re
import xml.etree.ElementTree as ET
import httplib2
import rfc3339

from apiclient.discovery import build
from oauth2client.client import Credentials

URL = 'http://vorlesungsplan.dhbw-mannheim.de/index.php?action=view&gid=3067001&uid=3967001&date={0}'
GRID = re.compile('<div class="ui-grid-e">.*(?=</div>.?</div>.?</body>)', re.DOTALL)

event = {
         'summary' : '',
         'location' : '',
         'start' : { 'dateTime' : '' },
         'end' :    { 'dateTime' : '' }
}

blocks = []
blocks.append(( datetime.date(2012, 9, 3), datetime.date(2012, 11, 23)  ))
blocks.append(( datetime.date(2013, 2, 18), datetime.date(2013, 5, 10)  ))
blocks.append(( datetime.date(2013, 9, 2), datetime.date(2013, 11, 22)  ))
blocks.append(( datetime.date(2014, 2, 17), datetime.date(2014, 5, 9)  ))

CALENDAR_ID = '9jehd9lrvaqpotvghihlpmj9t0@group.calendar.google.com'

def extract(dates):
    data = {}
    for m in dates:
        f = urllib2.urlopen(URL.format(m))
        s = re.findall(GRID, f.read())
        assert len(s) > 0
        data[m] = s[0]
        print('Requested: ', URL.format(m))
    return data

def parse(data):
    result = {}
    current = None
    for unused, html in data.items():
        root = ET.fromstring(html)
        for unused in root.iter('ul'):
            for item in root.iter('li'):
                if item.attrib:
                    current = item.text
                    result[current] = []
                else:
                    l = list(item)
                    result[current].append( (l[0].text, l[1].text, l[2].text))
    return result

def __create_datetime(s):
    p = re.split('[ \.:]', s)
    return rfc3339.rfc3339(datetime.datetime(int(p[3]), int(p[2]), int(p[1]), int(p[4]), int(p[5])))

def __create_service():
    with open('credentials', 'rw') as f:
        credentials = Credentials.new_from_json(f.read())

    http = httplib2.Http()
    http = credentials.authorize(http)
    
    return build('calendar', 'v3', http=http)

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
    
    now = datetime.datetime.now()
    
    for day in data.items():        
        for appointment in day[1]:            
            hours = appointment[0].split('-')
            assert len(hours) == 2
            event['start']['dateTime'] = __create_datetime('{0}.{1} {2}'.format(day[0], now.year, hours[0]))
            event['end']['dateTime'] = __create_datetime('{0}.{1} {2}'.format(day[0], now.year, hours[1]))
            event['summary'] = appointment[1]
            event['location'] = appointment[2]
            request = service.events().insert(calendarId=CALENDAR_ID, body=event)    
            print(unicode(event['summary'], "utf-8"))
            request.execute()
            
def timestamps(block):
    d = blocks[block][0]
    de = blocks[block][1]
    while d < de:
        yield time.mktime(d.timetuple())
        d = d + datetime.timedelta(7 - d.weekday())
                
if __name__ == "__main__":
    clear_calendar(0)
    update_calendar(parse(extract( timestamps(0) )))