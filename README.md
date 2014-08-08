TimeTablingAccessor
===================

provide a proper parsing and POST interface to UoL timetabling, to return iCal compatible data for integration into Google calendar, Outlook, etc.

This is supposed to run as CGI Python scripts in a web server environment. `ttparser.py` can generate a room booking calendar for a given room, `stafftt.py` generate a timetable calendar for a given member of staff.

## Room Bookings:

e.g. http://lcas.lincoln.ac.uk/tt/ttparser.py?room=MC3108 for room MC3108

## Staff Timetable:

e.g. http://lcas.lincoln.ac.uk/tt/stafftt.py?lecturer=003092 for *Marc Hanheide*'s (AD-ID 003092) timetable

