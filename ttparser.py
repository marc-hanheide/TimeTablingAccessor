#!/usr/bin/python
from StringIO import StringIO
from datetime import date, datetime, timedelta
import cgi
import cgitb
import logging

logging.basicConfig()

import requests
from lxml import etree
from icalendar import Calendar, Event, vText
from pytz import timezone

cgitb.enable()


class TTParser:
    _cal = Calendar()

    def __init__(self):
        self._cal = Calendar()
        self._cal.add('prodid', '-//University of Lincoln//Room TimeTable ICal Accessor//')
        self._cal.add('version', '2.0')
        self._baseUrl = "http://stafftimetables.lincoln.ac.uk/V2/UL/Reports/"


    def ical(self):
        d = date.today()
        for x in range(0, self._range):
            try:
                self.add_day(d + timedelta(x))
            except Exception as ex:
                logging.getLogger(__name__).warning(
                    'failed to add_day for ' + str(d + timedelta(x)) + ': ' + str(type(ex)) + ': ' + ex.message)
        return self._cal.to_ical()

    def create_event(self, name, room, the_day, time):
        tv = time.replace(' ', '').replace(':', '-').split('-')
        dBegin = datetime(the_day.year, the_day.month, the_day.day, int(tv[0]), int(tv[1]), tzinfo=self._tz_london)
        dEnd = datetime(the_day.year, the_day.month, the_day.day, int(tv[2]), int(tv[3]), tzinfo=self._tz_london)
        event = Event()
        event.add('summary', name)
        event.add('dtstart', dBegin)
        event.add('dtend', dEnd)
        event['location'] = vText(room)
        return event


class RoomTTParser(TTParser):
    _query_rooms = 'MC3204'
    _range = 30
    _tz_london = timezone('Europe/London')

    def __init__(self, room='MC3204', range=30):
        self._query_room = room
        self._range = range
        TTParser.__init__(self)

    def request(self, url, payload):
        r = requests.get(self._baseUrl + url, data=payload)
        html_parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), html_parser)
        return tree

    def add_day(self, the_day):
        payload = {'Room': self._query_room,
                   'TTDate': str(the_day.day) + '/' + str(the_day.month) + '/' + str(the_day.year),
                   'Step': '3',
                   'Site': 'BR-000'}
        tree = self.request("RoomTT.asp", payload)
        s = tree.xpath('/html/*/font/table/tr/td/table/tr/td/table/tr[2]/td/table[tr[2]/td]')
        if (len(s) > 0):
            room = tree.xpath('/html/*/font/table/tr/td/table/tr/td/table/tr[2]/td[1]/font/b/text()')[0]
            for se in s:
                name = se.xpath('tr[1]/td/font/text()')[0]
                time = se.xpath('tr[last()]/td/font/text()')[0]
                event = self.create_event(name, room, the_day, time)
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
print(tt.ical())
