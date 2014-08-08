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


class LecturerTTParser(TTParser):
    _lecturer = '003092'
    _tz_london = timezone('Europe/London')
    _start_date = date(2014, 9,15)

    def __init__(self, lecturer='003092'):
        self._lecturer = lecturer
        TTParser.__init__(self)

    def request(self, url, payload):
        r = requests.get(self._baseUrl + url, data=payload)
        html_parser = etree.HTMLParser()
        tree = etree.parse(StringIO(r.text), html_parser)
        return tree

    def date_to_query(self, d):
        td = d - self._start_date
	week = td.days // 7
	day_of_week = td.days % 7 + 1
        print week,day_of_week
	return week, day_of_week

    def query(self, day):
        week, day_of_week = self.date_to_query(day)
        payload = {'Lecturer': self._lecturer,
                   'Step': '3',
                   'FromWeek': week,
                   'ToWeek': week,
                   'FromDay': day_of_week,
                   'ToDay': day_of_week,
                   'Instance': 'All'}
        tree = self.request("LecturerTT.asp", payload)
	#print etree.tostring(tree,pretty_print=True)
        s = tree.xpath('//table[@rules="rows"]')
        events=[]
	for se in s:
		event={}
		#print etree.tostring(se,pretty_print=True)
		event['module'] = se.xpath('tr[1]/td//text()')[0]
                event['room'] = se.xpath('tr[2]/td//text()')[0]
                event['names'] = se.xpath('tr[3]/td//text()')[0]
                event['type'] = se.xpath('tr[4]/td//text()')[0]
                event['weeks'] = se.xpath('tr[5]/td//text()')[0]
                event['time'] = se.xpath('tr[6]/td//text()')[0]
		event['date'] = day
		events.append(event)
  		print event
        #if (len(s) > 0):
        #    room = tree.xpath('/html/*/font/table/tr/td/table/tr/td/table/tr[2]/td[1]/font/b/text()')[0]
        #    for se in s:
        #        name = se.xpath('tr[1]/td/font/text()')[0]
        #        time = se.xpath('tr[last()]/td/font/text()')[0]
        #        event = self.create_event(name, room, the_day, time)
        #        self._cal.add_component(event)


#cgi.test()
fs = cgi.FieldStorage()

if "lecturer" not in fs:
    lecturer = '003092'
else:
    lecturer = fs["lecturer"].value

#print(fs)

tt = LecturerTTParser(lecturer=lecturer)

print "Content-Type: text/calendar; charset=UTF-8"    # Print headers
#print "Content-Type: text/html; charset=UTF-8"    # Print headers
print ""                    # Signal end of headers
tt.query(date(2014,12,15))
#print(tt.ical())
