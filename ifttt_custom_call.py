from typing import Dict
import logging
import os
import requests
from fastapi import APIRouter, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ifttt_custom_call")

router = APIRouter()

logger.info("Starting IFTTT Webhook Environment Variable")
IFTTT_WEBHOOK = os.environ.get("IFTTT_WEBHOOK")
logger.info("Completed IFTTT Webhook Environment Variable")
logger.info("Starting IFTTT Event Name Environment Variable")
IFTTT_EVENT_NAME = "BitroidNotification"
logger.info("Completed IFTTT Event Name Environment Variable")

class IFTTTPayload(BaseModel):
    logger.debug("Defining IFTTTPayload model")
    value1: str = Field(..., example="Hello Hemanth Give a call back")
    value2: str = Field(..., example="to +91 0000000000")
    value3: str = Field(..., example="my self bitroid")


def send_ifttt_payload(payload: IFTTTPayload) -> requests.Response:
    if not IFTTT_WEBHOOK:
        logger.error("IFTTT_WEBHOOK environment variable is not configured")
        raise RuntimeError("IFTTT_WEBHOOK is not configured")

    url = f"https://maker.ifttt.com/trigger/{IFTTT_EVENT_NAME}/with/key/{IFTTT_WEBHOOK}"
    payload_data = payload.model_dump()
    logger.debug(f"Constructed payload: {payload_data}")

    logger.debug(f"Sending payload to IFTTT: {url}", extra={"payload": payload_data})

    response = requests.post(url, json=payload_data, timeout=10)
    logger.debug(f"IFTTT webhook response: {response.status_code} and {response.text}",
        extra={"status_code": response.status_code,
       "response_text": response.text,
        },
    )
    response.raise_for_status()
    return response


@router.post("/ifttt-send")
async def send_payload(payload: IFTTTPayload, request: Request) -> Dict[str, str]:
    client_host = request.client.host if request.client else "unknown"
    logger.debug(
        "Received request",
        extra={
            "client_host": client_host,
            "headers": dict(request.headers),
            "payload": payload.model_dump(),
        },
    )

    try:
        response = send_ifttt_payload(payload)
        return {
            "status": "success",
            "message": "Payload forwarded to IFTTT",
            "ifttt_status": str(response.status_code),
        }
    except RuntimeError as exc:
        logger.error("Configuration error", exc_info=exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except requests.RequestException as exc:
        logger.error("Failed to send payload to IFTTT", exc_info=exc)
        raise HTTPException(status_code=502, detail="Failed to send payload to IFTTT")

app = FastAPI(title="IFTTT Webhook Forwarder")
app.include_router(router)


# For debugging/direct run
if __name__ == "__main__":
    import uvicorn
    logger.debug("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
