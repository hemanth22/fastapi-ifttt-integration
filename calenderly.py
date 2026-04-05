import os
import json
import logging
from datetime import datetime
import certifi
from jinja2 import Template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Configure logging with debug mode
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def mongodb_fetch_calender_data():
    uri = os.environ.get("MONGODB_CLOUD")
    if not uri:
        logger.error("Error: MONGODB_CLOUD environment variable not set.")
        return []

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    try:
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        logger.debug("Successfully connected to MongoDB!")

        ## Specify your database and collection names here
        db = client["calenderly"]
        collection = db["reminders_cache"]
        
        # Example query using placeholder names
        documents = list(collection.find({}))
        logger.debug(f"Fetched {len(documents)} matching calendar documents.")
        return documents

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return []
    finally:
        client.close()

def generate_calendar_html(data):
    events = []
    seen_events = set()

    for item in data:
        date_str = item.get('message_date')
        if not date_str: continue
        
        # Format the date into ISO8601 for FullCalendar
        if isinstance(date_str, datetime):
            date_iso = date_str.isoformat()
        else:
            # Assumes format like '2026-02-12T01:42:00' or '2026-02-12 01:42:00'
            date_iso = str(date_str).replace(' ', 'T')

        title = str(item.get('message', 'Reminder'))
        day_key = date_iso.split('T')[0]
        msg_key = title.strip().lower()

        is_duplicate = (day_key, msg_key) in seen_events
        seen_events.add((day_key, msg_key))

        event_data = {
            'title': title,
            'start': date_iso
        }

        if is_duplicate:
            event_data['className'] = 'duplicate-event'

        events.append(event_data)

    events_json = json.dumps(events)

    template_str = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='utf-8' />
        <title>Interactive Calendar View</title>
        <!-- FullCalendar CDN -->
        <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js'></script>
        <style>
            body {
                margin: 40px 10px;
                padding: 0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f0f2f5;
                color: #333;
            }
            #calendar-container {
                background-color: #ffffff;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
                max-width: 1200px;
                margin: 0 auto;
            }
            
            /* Minimalist styling tweaks for Google/Outlook look */
            .fc-toolbar-title {
                font-size: 1.5em !important;
                font-weight: 600;
                color: #1a73e8;
            }
            .fc .fc-button-primary {
                background-color: #1a73e8 !important;
                border-color: #1a73e8 !important;
            }
            .fc .fc-button-primary:not(:disabled):active,
            .fc .fc-button-primary:not(:disabled).fc-button-active {
                background-color: #1557b0 !important;
                border-color: #1557b0 !important;
            }
            .fc-event {
                cursor: pointer;
                border-radius: 4px;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                padding: 2px;
            }
            .duplicate-event, .duplicate-event .fc-event-main {
                background-color: transparent !important;
                border-color: transparent !important;
                box-shadow: none !important;
                color: #888888 !important;
                font-weight: normal !important;
            }
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                var calendarEl = document.getElementById('calendar');
                var eventsData = {{ events_json | safe }};

                var calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: 'dayGridMonth',
                    headerToolbar: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
                    },
                    events: eventsData,
                    navLinks: true, // can click day/week names to navigate views
                    editable: false,
                    dayMaxEvents: true, // allow "more" link when too many events
                    eventTimeFormat: { // like '14:30'
                        hour: '2-digit',
                        minute: '2-digit',
                        meridiem: false
                    }
                });

                calendar.render();
            });
        </script>
    </head>
    <body>
        <div id='calendar-container'>
            <div id='calendar'></div>
        </div>
    </body>
    </html>
    """
    
    template = Template(template_str)
    html_output = template.render(events_json=events_json)
    
    return html_output

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/calenderview", response_class=HTMLResponse)
def get_calenderview():
    logger.debug("GET /calenderview request received.")
    data = mongodb_fetch_calender_data()
    if data:
        html_output = generate_calendar_html(data)
        logger.debug(f"Calendar HTML generated successfully with {len(data)} events.")
        return html_output
    else:
        logger.warning("No data found. Calendar creation skipped.")
        return "<html><body><h3>No data found. Calendar creation skipped.</h3></body></html>"

if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    uvicorn.run(app, host="0.0.0.0", port=8001)
