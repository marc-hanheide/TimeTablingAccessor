#!/usr/bin/python
from StringIO import StringIO
from datetime import date, datetime, timedelta
import cgi
import cgitb
import logging
from re import split

logging.basicConfig()

import requests
from lxml import etree
from icalendar import Calendar, Event, vText
from pytz import timezone

cgitb.enable()


class TTParser:
    _cal = Calendar()
    _tz_london = timezone('Europe/London')
    # the start date has to be the first Monday of the teaching period
    _start_date = date(2014, 9, 15)
    _range = 51 * 7

    def __init__(self):
        self._cal = Calendar()
        self._cal.add('prodid', '-//University of Lincoln//TimeTable//')
        self._cal.add('version', '2.0')
        self._baseUrl = "http://stafftimetables.lincoln.ac.uk/V2/UL/Reports/"

    def ical(self):
        #for x in range(0, self._range):
        for x in range(49, 70):
            try:
                self.query(self._start_date + timedelta(x))
            except Exception as ex:
                logging.getLogger(__name__).warning(
                    'failed to add_day for '
                    + str(self._start_date + timedelta(x))
                    + ': ' + str(type(ex)) + ': ' + ex.message)
        return self._cal.to_ical()

    def create_event(self, name, room, the_day, dBegin, dEnd):
        event = Event()
        event.add('summary', name)
        event.add('dtstart', dBegin)
        event.add('dtend', dEnd)
        event['location'] = vText(room)
        return event


class LecturerTTParser(TTParser):
    _lecturer = '003092'

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
        return week, day_of_week

    def query(self, day):
        week, day_of_week = self.date_to_query(day)
        if (day_of_week > 5):
            return
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

        for se in s:
            event = Event()

            #print etree.tostring(se,pretty_print=True)
            ev_module = se.xpath('tr[1]/td//text()')[0]
            ev_room = se.xpath('tr[2]/td//text()')[0]
            ev_names = se.xpath('tr[3]/td//text()')[0]
            ev_type = se.xpath('tr[4]/td//text()')[0]
            ev_weeks = se.xpath('tr[5]/td//text()')[0]
            ev_rawtime = se.xpath('tr[6]/td//text()')[0]
            splitstr = split('\W+', ev_rawtime)
            ev_start_time = datetime(day.year, day.month, day.day,
                                     int(splitstr[0]), int(splitstr[1]),
                                     tzinfo=self._tz_london)
            ev_end_time = datetime(day.year, day.month, day.day,
                                   int(splitstr[2]), int(splitstr[3]),
                                   tzinfo=self._tz_london)

            event.add('summary', ev_module + ' - ' + ev_type)
            event.add('dtstart', ev_start_time)
            event.add('dtend', ev_end_time)
            event['location'] = vText(ev_room)
            event['description'] = vText('names: ' + ev_names
                                         + ', weeks: ' + ev_weeks)
            self._cal.add_component(event)
        



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
tt.query(date(2014, 12, 15))
print(tt.ical())
