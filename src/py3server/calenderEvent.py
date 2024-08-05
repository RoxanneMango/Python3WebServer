# imports
#from icalendar import Calendar, Event, vCalAddress, vText
import icalendar
from datetime import datetime
import pytz
from pathlib import Path
import os

class CalenderEvent():
	
	def __init__(self, name, email, description, uid):
		print("Event!");
		# init the calendar
		cal = icalendar.Calendar();
		# Some properties are required to be compliant
		cal.add('prodid', '-//Production//id//');
		cal.add('version', '1.0');
				
		# Add subcomponents
		event = icalendar.Event();
		event.add('name', name);
		event.add('description', description);
		event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc));
		event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc));
		 
		# Add the organizer
		organizer = icalendar.vCalAddress('MAILTO:'+email)
		organizer.params['name'] = icalendar.vText('John Doe');
		organizer.params['role'] = icalendar.vText('CEO');		 

		# Add parameters of the event
		event['organizer'] = organizer;
		event['location'] = icalendar.vText('New York, USA')
		 
		event['uid'] = uid;
		event.add('priority', 5)
		attendee = icalendar.vCalAddress('MAILTO:rdoe@example.com')
		attendee.params['name'] = icalendar.vText('Richard Roe')
		attendee.params['role'] = icalendar.vText('REQ-PARTICIPANT')
		event.add('attendee', attendee, encode=0)
		 
		attendee = icalendar.vCalAddress('MAILTO:jsmith@example.com')
		attendee.params['name'] = icalendar.vText('John Smith')
		attendee.params['role'] = icalendar.vText('REQ-PARTICIPANT')
		event.add('attendee', attendee, encode=0)
		 
		# Add the event to the calendar
		cal.add_component(event)
		
		# Write to disk
		directory = Path.cwd() / 'MyCalendar'
		try:
		   directory.mkdir(parents=True, exist_ok=False)
		except FileExistsError:
		   print("Folder already exists")
		else:
		   print("Folder was created")
		 
		f = open(os.path.join(directory, 'example.ics'), 'wb')
		f.write(cal.to_ical())
		f.close()		
		
