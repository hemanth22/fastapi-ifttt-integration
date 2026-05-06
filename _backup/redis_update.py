import redis
import os
import psycopg2
import logging
import sys
import json
from datetime import datetime
import pytz


# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
POSTGRES_HOST = os.environ.get('postgres_host')
POSTGRES_DB = os.environ.get('postgres_db')
POSTGRES_PORT = os.environ.get('postgres_port')
POSTGRES_USER = os.environ.get('postgres_user')
POSTGRES_PASSWORD = os.environ.get('postgres_password')

# Redis variables
redis_host = os.environ.get('redis_host')
redis_port = os.environ.get('redis_port')
redis_password = os.environ.get('redis_password')
redis_username = os.environ.get('redis_username')

# Global Redis client
redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    username=redis_username,
    password=redis_password,
    decode_responses=True
)


def get_db_connection():
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

def get_postgres_data():
    """
    Connects to PostgreSQL and fetches reminders for the current date.
    Returns a list of dictionaries or None if error/no data.
    """
    connection = get_db_connection()
    if not connection:
        logger.error("Database connection failed during processing.")
        return None

    logger.info("Database connection successful.")
    
    # Timezone setup
    try:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        current_dt = datetime.now(ist_timezone)
        formatted_date = current_dt.strftime("%Y-%m-%d")
        logger.info(f"Processing for date: {formatted_date}")
    except Exception as e:
        logger.error(f"Timezone error: {str(e)}")
        connection.close()
        return None

    cursor = connection.cursor()
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

    try:
        logger.info(f"Executing query for date: {formatted_date}")
        cursor.execute(query, (formatted_date,))
        row = cursor.fetchone()
        
        if row and row[0]:
            messages = row[0]
            logger.info(f"Fetched {len(messages)} messages from DB.")
            return messages
        else:
            logger.info("No messages found for today.")
            return []

    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def update_redis(data):
    """
    Updates Redis with the provided data.
    """
    try:
        # Check connection

        
        logger.info(f"Redis connection check {redis_client.ping()}")

        if data:
             # Convert to JSON string for Redis
            messages_json = json.dumps(data)
            
            # Store in Redis
            redis_client.delete('remainder_ifttt')
            logger.info("Deleted 'remainder_ifttt' key from Redis.")
            logger.debug(f"Verify purge: {redis_client.get('remainder_ifttt')}")
            logger.debug(f"Data to be stored in Redis: {messages_json}")
            redis_client.set('remainder_ifttt', messages_json)
            logger.info("Successfully updated 'remainder_ifttt' key in Redis.")
            logger.debug(f"Verify update: {redis_client.get('remainder_ifttt')}")
        else:
            logger.info("Data is empty or None. Clearing Redis key.")
            redis_client.delete('remainder_ifttt')
            
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
    except Exception as e:
         logger.error(f"Error updating Redis: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    data = get_postgres_data()
    if data is not None:
        update_redis(data)
    else:
        logger.error("Failed to fetch data from PostgreSQL.")
        sys.exit(1)