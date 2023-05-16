// paste the following code into a google script.

const log = console.log

// specify the email address you're filtering
const senderEmail = 'REPLACE@gmail.com'

const CalendarId = 'Go into google calendar settings and get the calendar id. then paste it here'

const CalendarObj = Calendar.getCalendarById(CalendarId)
log(CalendarObj)

const oneDayInMinutes = 60 * 24

function processEmail() {
  const query = 'from:' + senderEmail;

  // list all msgs from sender
  const response = Gmail.Users.Messages.list('me', {q: query});

  console.log(response)

  if (response.messages) {
    for (let i = 0; i < response.messages.length; i++) {
      const message = response.messages[i];
      const msg = Gmail.Users.Messages.get('me', message.id);
      const headers = msg.payload.headers;

      for (let j = 0; j < headers.length; j++) {
        const header = headers[j];

        if (header.name == 'Subject') {
          const openMailSubject = header.value;
          const match = openMailSubject.match(/Hooray! You have a new class at ([a-zA-Z]{3}, [a-zA-Z]{3} \d{1,2}, \d{4} \d{1,2}:\d{2} [AP]M [a-zA-Z ]+)$/);

          if (match) {
            const startTimeStr = match[1];
            // log(startTimeStr)

            const startTimeUtc = new Date(startTimeStr.replace('New York Timezone', '-0400'));
            
            // replace with your timezone
            const myTimeZone = 'US/Eastern'; 
            const startTimeEastern = Utilities.formatDate(startTimeUtc, myTimeZone, 'yyyy-MM-dd\'T\'HH:mm:ss');
            const endTimeEastern = Utilities.formatDate(new Date(startTimeUtc.getTime() + 60 * 60 * 1000), myTimeZone, 'yyyy-MM-dd\'T\'HH:mm:ss');

            const existingEvents = Calendar.getEvents(startTimeEastern, endTimeEastern)
            log(existingEvents)

           
            
            const event = {
              'summary': '',
              'location': '',
              'description': '',
              'start': {
                'dateTime': startTimeEastern,
                'timeZone': myTimeZone,
              },

              'end': {
                'dateTime': endTimeEastern,
                'timeZone': myTimeZone,
              },

              'reminders': {
                'useDefault': false,
                'overrides': [
                  { 'method': 'popup', 'minutes': oneDayInMinutes * 2 },
                  { 'method': 'popup', 'minutes': oneDayInMinutes },
                  { 'method': 'popup', 'minutes': 10 }
                ]
              }
            };

            // ADD EVENT TO CALENDAR
            Calendar.Events.insert(event, CalendarId);

          }
        }
      }
    }
  } else {
    Logger.log('No messages found.');
  }
}
