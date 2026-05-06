"""Basic connection example.
"""

import redis
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_redis_data():
    try:
        redis_host = os.environ.get('redis_host')
        redis_port = os.environ.get('redis_port')
        redis_password = os.environ.get('redis_password')
        redis_username = os.environ.get('redis_username')
        logger.info("Environment variables loaded successfully.")

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            username=redis_username,
            password=redis_password,
        )
        logger.info("Redis connection successful.")
        result = r.get('remainder_ifttt')
        logger.info("Redis result fetched successfully.")
        logger.info(f"Redis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return None

if __name__ == "__main__":
    get_redis_data()
