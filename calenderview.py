import os
import psycopg2
import logging
import sys
import json
from datetime import datetime
import pytz
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables
POSTGRES_HOST = os.environ.get('postgres_host')
POSTGRES_DB = os.environ.get('postgres_db')
POSTGRES_PORT = os.environ.get('postgres_port')
POSTGRES_USER = os.environ.get('postgres_user')
POSTGRES_PASSWORD = os.environ.get('postgres_password')

def get_db_connection_for_calender():
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

def get_postgres_data_for_calender():
    """
    Connects to PostgreSQL and fetches reminders for the current date.
    Returns a list of dictionaries or None if error/no data.
    """
    connection = get_db_connection_for_calender()
    if not connection:
        logger.error("Database connection failed during processing.")
        return None

    logger.info("Database connection successful.")
    
    # Timezone setup
    try:
        ist_timezone = pytz.timezone("Asia/Kolkata")
        logger.info(f"Timezone set to IST: {ist_timezone}")
        current_dt = datetime.now(ist_timezone)
        logger.info(f"Current date and time: {current_dt}")
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
        ORDER BY
            message_date
    ) t;
    """

    try:
        logger.info(f"Executing query for date: {formatted_date}")
        cursor.execute(query)
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

def mongodb_fetch_calender_data():
    mongodb_uri = os.environ.get("MONGODB_CLOUD")
    if not mongodb_uri:
        logger.info("Error: MONGODB_CLOUD environment variable not set.")
        return

    # Create a new client and connect to the server
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

    try:
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!\n")

        ## Specify your database and collection names here
        db = client["calenderly"]
        collection = db["reminders_cache"]
        
        # Example query using placeholder names
        documents = collection.find({})
        result = []
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            result.append(doc)
        return result

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None
    finally:
        client.close()

def update_mongodb_data(data):
    """
    Mongodb: Update mongoDB cache with json data stored in postgres
    """
    try:
        mongodb_uri = os.environ.get("MONGODB_CLOUD")
        if not mongodb_uri:
            logger.error("Error: MONGODB_CLOUD environment variable not set.")
            return
            
        client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        
        # Connect to your preferred database and collection
        db = client['calenderly']
        collection = db['reminders_cache']
        
        # Clear the old cache
        collection.delete_many({})
        
        # Insert the new data
        if data:
            if isinstance(data, list):
                collection.insert_many(data)
            elif isinstance(data, dict):
                collection.insert_one(data)
            else:
                logger.warning("Data format not recognized. Expected list or dict.")
                
        logger.info("Successfully updated MongoDB cache with PostgreSQL data.")
        
    except Exception as e:
        logger.error(f"Error updating MongoDB: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    data = get_postgres_data_for_calender()
    if data is not None:
        update_mongodb_data(data)
        mongodb_fetch_calender_data()
    else:
        logger.error("Failed to fetch data from PostgreSQL.")
        sys.exit(1)
