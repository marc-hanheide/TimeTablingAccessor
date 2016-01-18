#!/usr/bin/python
from StringIO import StringIO
from datetime import date, datetime, timedelta
import csv
import cgi
import cgitb
import re
import logging
import pyfscache
import requests
from icalendar import Calendar, Event, vText
from pytz import timezone
from re import split

logging.basicConfig()

cgitb.enable()

cache_it = pyfscache.FSCache('./cache',
                             days=7)
#cache_it = pyfscache.FSCache('/var/www/tt/cache',
#                             days=7)


class TTParser:
    _cal = Calendar()
    _tz_london = timezone('Europe/London')
    # the start date has to be the first Monday of the teaching period
    _start_date = date(2015, 9, 14)


    def __init__(self):
        self._cal = Calendar()
        self._cal.add('prodid', '-//University of Lincoln//TimeTable//')
        self._cal.add('version', '2.0')
        self._baseUrl = "http://stafftimetables.lincoln.ac.uk/V2/UL/Reports/"

    def ical(self):
        self.query()
        return self._cal.to_ical()


class SubjectTTParser(TTParser):

    def __init__(self):
        TTParser.__init__(self)

    def request(self, url, payload):
        k = str(payload)
        if k in cache_it:
            t = cache_it[k]
        else:
            r = requests.get(self._baseUrl + url, data=payload)
            t = r.text
            cache_it[k] = t
        #print t
        cr = csv.reader(StringIO(t),dialect='excel-tab')
        return cr

    def dow_weeks_to_dates(self, dow, weeks):
        dow_map = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6
        }
        periods = re.split('[, ]+', weeks)
        all_weeks = []
        for p in periods:
            r = re.split('[-]+', p)
            if len(r) > 1:
                all_weeks = all_weeks + range(int(r[0]), int(r[1])+1)
            else:
                all_weeks.append(int(r[0]))
        return [self._start_date + timedelta(w * 7 + dow_map[dow]) for w in all_weeks]
        #return [(w * 7 + dow_map[dow]) for w in all_weeks]


    def query(self):
        payload = {'Subject': 'CMP',
                   'DeskTop': 'Excel',
                   'Step': '3',
                   'FromWeek': 0,
                   'ToWeek': 52,
                   'Instance': 'All',
                   'Level': 'All',
                   'Seq': 'Unit'}
        r = self.request("SubjectTT.asp", payload)
        row_no = 0
        for row in r:
            row_no += 1
            if row_no <= 4:
                continue

            module, title, session, subsession, dow, time_string, room, lecturer, weeks = row
            #print module, weeks, self.dow_weeks_to_dates(dow, weeks)


            splitstr = split('\W+', time_string)

            for d in self.dow_weeks_to_dates(dow, weeks):
                event = Event()
                ev_start_time = datetime(d.year, d.month, d.day,
                                         int(splitstr[0]), int(splitstr[1]),
                                         tzinfo=self._tz_london)
                ev_end_time = datetime(d.year, d.month, d.day,
                                       int(splitstr[2]), int(splitstr[3]),
                                       tzinfo=self._tz_london)



                event.add('summary', module + ': ' + title + ' - ' + session)
                event.add('dtstart', ev_start_time)
                event.add('dtend', ev_end_time)
                event['location'] = vText(room)
                event['description'] = vText('names: ' + lecturer
                                             + ', weeks: ' + weeks
                                             + ', session: ' + subsession)
                self._cal.add_component(event)



            # #print etree.tostring(se,pretty_print=True)
            # ev_room = se.xpath('tr[2]/td//text()')[0]
            # ev_names = se.xpath('tr[3]/td//text()')[0]
            # ev_type = se.xpath('tr[4]/td//text()')[0]
            # ev_weeks = se.xpath('tr[5]/td//text()')[0]
            # ev_rawtime = se.xpath('tr[6]/td//text()')[0]
            # event.add('summary', ev_module + ' - ' + ev_type)
        



#cgi.test()
fs = cgi.FieldStorage()


tt = SubjectTTParser()

print "Content-Type: text/calendar; charset=UTF-8"    # Print headers
#print "Content-Type: text/html; charset=UTF-8"    # Print headers
print ""                    # Signal end of headers
print(tt.ical())
