from fastapi import FastAPI, Request, Form, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import asyncio
from redis_update import get_postgres_data, update_redis
import asyncpg
import os
import requests
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

POSTGRES_USER = os.environ.get('postgres_user')
POSTFRES_PASSWORD = os.environ.get('postgres_password')
POSTFRES_DBNAME = os.environ.get('postgres_db')
POSTFRES_HOSTNAME = os.environ.get('postgres_host')
POSTFRES_PORT = os.environ.get('postgres_port')

logger.info("Environment variables loaded.")

DB_CONFIG = {
    "user": POSTGRES_USER,
    "password": POSTFRES_PASSWORD,
    "database": POSTFRES_DBNAME,
    "host": POSTFRES_HOSTNAME,
    "port": POSTFRES_PORT
}

logger.info("Parsed DB Config.")


async def call_insert_remainder_ifttt(p_date: str, p_message: str):
    logger.info("Insert requested received")
    logger.info(f"Date: {p_date}, Message: {p_message}")
    conn = await asyncpg.connect(**DB_CONFIG)
    logger.info("DB Connection established.")
    try:
        logger.info("Executing SQL Query.")
        await conn.execute("SELECT insert_ifttt_remainder($1, $2);", p_date, p_message)

        logger.info("SQL Query executed successfully.")
    finally:
        await conn.close()
        logger.info("DB Connection closed.")

app = FastAPI()
logger.info("FastAPI app created.")
templates = Jinja2Templates(directory="templates")
logger.info("Jinja2 Templates loaded.")

@app.get("/ifttt-remainders", response_class=HTMLResponse)
async def read_form(request: Request):
    logger.info("Read form requested.")
    return templates.TemplateResponse("ifttt_form.html", {"request": request})

@app.post("/submit-ifttt", response_class=HTMLResponse)
async def handle_form(
    request: Request,
    date_input: datetime = Form(...),
    message: str = Form(...)
):
    logger.info("Form submission received.")
    formatted_date = date_input.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Formatted date: {formatted_date}")
    await call_insert_remainder_ifttt(formatted_date, message)
    logger.info("Remainder inserted program completed.")

    # Trigger Redis update (asynchronous to not block response too much, but we wait for it here to ensure consistency)
    try:
        logger.info("Triggering Redis update...")
        # Run sync functions in thread
        data = await asyncio.to_thread(get_postgres_data)
        if data:
            await asyncio.to_thread(update_redis, data)
            logger.info("Redis update triggered successfully.")
        else:
             # If no data, we might still want to update redis to clear it or it might be an error. 
             # redis_update.get_postgres_data returns [] if no messages, so we should update with empty list to clear redis if that's the logic.
             # but get_postgres_data returns None on error.
             if data is not None:
                 await asyncio.to_thread(update_redis, data)
                 logger.info("Redis update triggered (empty data).")
             else:
                 logger.error("Failed to fetch data from postgresql to Redis update.")

    except Exception as e:
        logger.error(f"Error triggering Redis update: {e}")

    return templates.TemplateResponse("ifttt_form.html", {
        "request": request,
        "submitted": True,
        "date_input": date_input,
        "message": message
    })