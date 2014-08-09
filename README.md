TimeTablingAccessor
===================

provides iCal access to UoL timetabling. Return iCal compatible data for integration into Google calendar, Outlook, etc.

This is supposed to run as CGI Python scripts in a web server environment (currently at http://lcas.lincoln.ac.uk/tt/). `ttparser.py` can generate a room booking iCal calendar for a given room (as POST param), `stafftt.py` generates a timetable calendar for a given member of staff (from their Active Directory ID, e.g. 003092).

## Room Bookings:

e.g. http://lcas.lincoln.ac.uk/tt/ttparser.py?room=MC3108 for room MC3108

## Staff Timetable:

e.g. http://lcas.lincoln.ac.uk/tt/stafftt.py?lecturer=003092 for *Marc Hanheide*'s (AD-ID 003092) timetable

## Use in Google Calendar:

Under "Other Calendars", select "Add by URL". Enter the respective URL (see above). *Note:* Google caches your the calendar, and only updates it every few hours or so. So, timetable changes are not immediately visible in there.