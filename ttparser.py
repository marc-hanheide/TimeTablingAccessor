from StringIO import StringIO

import requests
from lxml import etree
from icalendar import Calendar, Event, vText


#payload = "Room=MC3204&TTDate=27%2F1%2F2014&Site=BR-000&Step=3"
import time
from datetime import date, datetime
from pytz import timezone

today = date.today()

payload = {'Room': 'MC3204', 'TTDate': str(today.day + 2) + '/' + str(today.month) + '/' + str(today.year), 'Step': '3',
           'Site': 'BR-000'}

r = requests.get("http://stafftimetables.lincoln.ac.uk/V2/UL/Reports/RoomTT.asp", data=payload)

htmlparser = etree.HTMLParser()
tree = etree.parse(StringIO(r.text), htmlparser)

cal = Calendar()
tz_london = timezone('Europe/London')
s = tree.xpath('/html/body/font/table/tr/td/table/tr/td/table/tr[2]/td/table[tr[2]/td]')
room = tree.xpath('/html/body/font/table/tr/td/table/tr/td/table/tr[2]/td[1]/font/b/text()')[0]
print(room)
for se in s:
    event = Event()
    name = se.xpath('tr[1]/td/font/text()')
    #print(name[0])
    event.add('summary', name[0])
    time = se.xpath('tr[last()]/td/font/text()')
    #print(time[0])
    tv = time[0].replace(' ', '').replace(':', '-').split('-')
    dBegin = datetime(today.year, today.month, today.day, int(tv[0]), int(tv[1]), tzinfo=tz_london)
    dEnd = datetime(today.year, today.month, today.day, int(tv[2]), int(tv[3]), tzinfo=tz_london)
    event.add('dtstart', dBegin)
    event.add('dtend', dEnd)
    event['location'] = vText(room)
    cal.add_component(event)

print(cal.to_ical())

