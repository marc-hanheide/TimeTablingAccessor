#!/usr/bin/python
from StringIO import StringIO

import requests
from lxml import etree
from icalendar import Calendar, Event, vText


#payload = "Room=MC3204&TTDate=27%2F1%2F2014&Site=BR-000&Step=3"
from datetime import date, datetime, timedelta
from pytz import timezone

import cgi
import cgitb

cgitb.enable()


class RoomTTParser:
    _cal = Calendar()
    _query_rooms = 'MC3204'
    _range = 30
    _tz_london = timezone('Europe/London')

    def __init__(self, room='MC3204', range=30):
        self._query_room = room
        self._range = range
        self._cal = Calendar()
        self._cal.add('prodid', '-//University of Lincoln//Room TimeTable ICal Accessor//')
        self._cal.add('version', '2.0')


def get_ical(self):
    d = date.today()
    for x in range(0, self._range):
        self.addDay(d + timedelta(x))
    return self._cal.to_ical()


def addDay(self, today):
    payload = {'Room': self._query_room, 'TTDate': str(today.day) + '/' + str(today.month) + '/' + str(today.year),
               'Step': '3',
               'Site': 'BR-000'}
    r = requests.get("http://stafftimetables.lincoln.ac.uk/V2/UL/Reports/RoomTT.asp", data=payload)
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(r.text), htmlparser)


    #	tmp=tree.getroot().xpath('/html/*/font/table');
    #	print(len(tmp))
    #	print(tmp[0].tag)
    #        print(etree.tostring(tmp[0]))

    s = tree.xpath('/html/*/font/table/tr/td/table/tr/td/table/tr[2]/td/table[tr[2]/td]')
    if (len(s) > 0):
        room = tree.xpath('/html/*/font/table/tr/td/table/tr/td/table/tr[2]/td[1]/font/b/text()')[0]
        for se in s:
            event = Event()
            name = se.xpath('tr[1]/td/font/text()')
            #print(name[0])
            event.add('summary', name[0])
            time = se.xpath('tr[last()]/td/font/text()')
            #print(time[0])
            tv = time[0].replace(' ', '').replace(':', '-').split('-')
            dBegin = datetime(today.year, today.month, today.day, int(tv[0]), int(tv[1]), tzinfo=self._tz_london)
            dEnd = datetime(today.year, today.month, today.day, int(tv[2]), int(tv[3]), tzinfo=self._tz_london)
            event.add('dtstart', dBegin)
            event.add('dtend', dEnd)
            event['location'] = vText(room)
            self._cal.add_component(event)


#cgi.test()
fs = cgi.FieldStorage()

if "room" not in fs:
    room = 'MC3204'
else:
    room = fs["room"].value

if "range" not in fs:
    rge = 14
else:
    rge = int(fs["range"].value)

#print(fs)

tt = RoomTTParser(room=room, range=rge)

print "Content-Type: text/calendar; charset=UTF-8"    # Print headers
#print "Content-Type: text/html; charset=UTF-8"    # Print headers
print ""                    # Signal end of headers
print(tt.get_ical())
