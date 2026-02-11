import os
import psycopg2
import requests
import logging
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
import pytz
from fastapi import FastAPI, HTTPException
from typing import List, Optional

# Configure Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment Variables
POSTGRES_HOST = os.environ.get('postgres_host')
POSTGRES_DB = os.environ.get('postgres_db')
POSTGRES_PORT = os.environ.get('postgres_port')
POSTGRES_USER = os.environ.get('postgres_user')
POSTGRES_PASSWORD = os.environ.get('postgres_password')
IFTTT_WEBHOOK_KEY = os.environ.get('IFTTT_WEBHOOK')

logger.debug("Environment variables loaded.")

def get_db_connection():
    # logger.debug("Attempting to connect to the database...") # Reduced noise
    try:
        connection = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return connection
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return None

def make_iftttcall(message_info: str):
    logger.debug(f"Preparing IFTTT call for message: {message_info}")
    if not IFTTT_WEBHOOK_KEY:
        logger.error("IFTTT_WEBHOOK key is missing.")
        return False, "IFTTT_WEBHOOK key missing"

    base_url = f'https://maker.ifttt.com/trigger/BitroidNotification/with/key/{IFTTT_WEBHOOK_KEY}'
    payload = {
      'value1': 'this is a remainder',
      'value2': message_info,
      'value3': 'End of Comms'
    }
    logger.debug(f"IFTTT Payload: {payload}")

    try:
        #logger.debug(f"Sending POST request to {base_url}")
        logger.debug(f"Sending POST request to IFTTT Webhook : https://maker.ifttt.com/trigger/BitroidNotification/with/key")
        response = requests.post(base_url, json=payload)
        logger.debug(f"IFTTT Response Status Code: {response.status_code}")
        if response.status_code == 200:
            logger.info('JSON payload sent successfully to IFTTT Webhook')
            return True, "Success"
        else:
            logger.error(f'Failed to send JSON payload. Status code: {response.status_code}')
            return False, f"Failed with status {response.status_code}"
    except Exception as e:
        logger.error(f'An error occurred during IFTTT call: {str(e)}')
        return False, str(e)

def process_reminders_logic():
    """
    Core logic to check reminders. Returns a dictionary with results.
    """
    # Timezone setup
    try:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        current_dt = datetime.now(ist_timezone)
        formatted_date = current_dt.strftime("%Y-%m-%d")
        current_time_min = current_dt.strftime("%Y-%m-%dT%H:%M") # Match up to minute
    except Exception as e:
        logger.error(f"Timezone error: {str(e)}")
        return {"error": str(e)}

    connection = get_db_connection()
    if not connection:
        logger.error("Database connection failed during processing.")
        return {"error": "Database connection failed"}

    results_summary = []
    
    try:
        cursor = connection.cursor()
        # Using json_agg as requested
        query = """
        SELECT json_agg(t) FROM (
            SELECT
                message_date,
                message
            FROM
                remainder_ifttt
            WHERE
                to_char(message_date,'YYYY-MM-DD') = %s
        ) t;
        """
        # logger.debug(f"Executing query params: ({formatted_date},)")
        cursor.execute(query, (formatted_date,))
        row = cursor.fetchone()
        
        if not row or not row[0]:
            logger.info("No messages found for this date (NULL result).")
            return {"message": "No messages found for this date.", "date": formatted_date, "current_time": current_time_min, "processed_messages": []}

        messages = row[0] # List of dicts
        logger.debug(f"Fetched {len(messages)} messages for today.")

        for msg_item in messages:
            msg_date_str = msg_item.get('message_date')
            msg_content = msg_item.get('message')
            
            # Simple string matching up to minute
            if msg_date_str and msg_date_str.startswith(current_time_min):
                logger.info(f"Time match! Triggering IFTTT for: {msg_content}")
                success, status_msg = make_iftttcall(msg_content)
                results_summary.append({
                    "message": msg_content,
                    "message_date": msg_date_str,
                    "ifttt_sent": success,
                    "status": status_msg
                })
            else:
                logger.debug(f"Time mismatch. Current: {current_time_min}, Msg: {msg_date_str}")
                pass
            
    except psycopg2.Error as e:
        logger.error(f"Database error executing query: {str(e)}")
        return {"error": f"Database error: {str(e)}"}
    finally:
        if connection:
            cursor.close()
            connection.close()
            
    if results_summary:
        logger.info(f"Processed {len(results_summary)} matching reminders.")
    
    return {"date": formatted_date, "current_time": current_time_min, "processed_messages": results_summary}

async def scheduler_loop():
    logger.info("Scheduler started. Running every 60 seconds.")
    while True:
        try:
            logger.info("Scheduler: Checking reminders...")
            # Run sync function in thread to avoid blocking event loop
            result = await asyncio.to_thread(process_reminders_logic)
            logger.debug(f"Scheduler check result: {result.get('processed_messages')}")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        
        # Wait for next minute
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start scheduler
    task = asyncio.create_task(scheduler_loop())
    yield
    # Shutdown: Cancel scheduler
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Scheduler task cancelled.")

app = FastAPI(lifespan=lifespan)

@app.get("/check-reminders")
async def check_reminders():
    logger.debug("Received manual request for /check-reminders")
    # Run sync DB logic in threadpool to avoid blocking event loop
    result = await asyncio.to_thread(process_reminders_logic)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

# For debugging/direct run
if __name__ == "__main__":
    import uvicorn
    logger.debug("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
