# Copilot Instructions — fastapi-ifttt-integration

## What this project is

A FastAPI service that stores timed reminders and sends them as IFTTT push notifications. It runs as a **serverless app on Vercel**, so there is no long-running process or in-app scheduler.

Data flow:

1. **Write:** the user submits the HTML form (`/ifttt-remainders` → `POST /submit-ifttt`). The app calls the PL/pgSQL function `insert_ifttt_remainder(p_date, p_message)` in **PostgreSQL** through `asyncpg`.
2. **Cache (today's reminders):** `redis_update.get_postgres_data()` fetches today's rows (IST), and `update_redis()` stores them as a JSON string under the Redis key `remainder_ifttt`.
3. **Cache (all reminders, for the calendar):** `calenderview.get_postgres_data_for_calender()` fetches every row, and `update_mongodb_data()` replaces the MongoDB collection `calenderly.reminders_cache`.
4. **Fire:** an external cron (Vercel Cron) calls `GET /check-reminders`. `main.process_reminders_logic()` reads `remainder_ifttt` from Redis, compares each `message_date` with the current IST time **to the minute** (`YYYY-MM-DDTHH:MM` prefix match), and posts matches to the IFTTT Maker webhook.
5. **View:** `GET /calenderview` renders a FullCalendar page (inline Jinja2 template) from the MongoDB cache.

PostgreSQL is the source of truth. Redis and MongoDB are derived caches that are rebuilt in full; they are never updated incrementally.

## File map

| File | Role |
|---|---|
| `main.py` | Vercel entrypoint. Creates `app`, includes the other routers, and defines `/`, `/check-reminders`, `/update-redis`, `/update-mongodb-calender`, `/fetch-mongodb-calender`, `/status_code`, `/health`. Holds `make_iftttcall()` and `process_reminders_logic()`. |
| `redis_update.py` | Module-level global `redis_client`, plus `get_postgres_data()` (today only) and `update_redis(data)`. Can be run as a script. |
| `calenderview.py` | Postgres → MongoDB sync (`get_postgres_data_for_calender`, `update_mongodb_data`, `mongodb_fetch_calender_data`). Can be run as a script. |
| `calenderly.py` | `APIRouter` for `/calenderview` (HTML calendar). Has its **own** `mongodb_fetch_calender_data()` that differs from the one in `calenderview.py`. |
| `ifttt_web_interface.py` | Defines a separate `FastAPI()` app whose `.router` is included by `main.py`. Serves the form and handles submission, then refreshes the Redis and MongoDB caches inline. |
| `ifttt_custom_call.py` | `APIRouter` for `POST /ifttt-send`, which forwards an arbitrary `{value1, value2, value3}` payload to IFTTT. Uses a Pydantic model and `raise_for_status()`. |
| `templates/ifttt_form.html` | Jinja2 form template, loaded from the relative `templates` directory. |
| `insert_ifttt_remainder.plpgsql` | DB function that inserts into `remainder_ifttt(message_date TIMESTAMP, message TEXT)`. It catches its own errors and **returns** an error string instead of raising. |
| `usage.plpgsql` | Example call. |
| `test_redis.py` | Manual Redis connectivity script. This is **not** a pytest suite. |
| `vercel.json` | Routes everything to `main.py` through `@vercel/python`. |
| `.github/workflows/vercel_deploy.yml` | Deploys to Vercel production on push to `releasev5` and on PRs to `main`. |

## Configuration (environment variables)

The names are case-sensitive and the casing is inconsistent. Keep them exactly as they are:

- PostgreSQL: `postgres_host`, `postgres_db`, `postgres_port`, `postgres_user`, `postgres_password` (lowercase)
- Redis: `redis_host`, `redis_port`, `redis_username`, `redis_password` (lowercase)
- IFTTT: `IFTTT_WEBHOOK` (the Maker webhook key)
- MongoDB: `MONGODB_CLOUD` (Atlas connection URI, used with `certifi` for TLS)

The IFTTT event name is hard-coded as `BitroidNotification`. Never hard-code secrets. Never log the webhook key or a full webhook URL: `main.make_iftttcall` deliberately logs the URL without the key, so keep it that way.

## Conventions to follow

- **Keep the misspelled names as they are.** `remainder` (for reminder) and `calender` (for calendar) appear in routes, the Redis key, the Postgres table and function, the MongoDB db and collection, and function names. Renaming any of them breaks deployed clients, cron jobs, and stored data. Use the existing spellings in new code that touches these resources.
- **Timezone:** all "now" and "today" logic uses `pytz.timezone("Asia/Kolkata")`. Stored `message_date` values are naive IST timestamps.
- **Async endpoints, sync I/O:** `psycopg2`, `redis`, and `pymongo` calls are blocking. Inside `async def` routes, wrap them with `await asyncio.to_thread(fn, ...)`. Only the form insert uses `asyncpg` directly.
- **Helper return contract:** data-fetch helpers return `None` on error and `[]` when there is no data. Callers must tell the two apart: `[]` should still clear or refresh the cache, and `None` is a failure. Endpoints turn `None` into `HTTPException(500)`.
- **Endpoint error pattern:** use `try` / `except HTTPException: raise` / `except Exception as e: logger.error(...); raise HTTPException(500, detail=str(e))`. For upstream IFTTT failures, return `502` (see `ifttt_custom_call.py`).
- **Connections:** open a Postgres or Mongo connection per call and close it in `finally`. Redis uses the shared module-level `redis_client` (`decode_responses=True`).
- **SQL:** always use parameterized queries (`%s` for psycopg2, `$1` for asyncpg). Queries return rows through `json_agg(...)`, so `fetchone()[0]` is already a list of dicts.
- **Logging:** each module uses `logger = logging.getLogger(__name__)` with f-string messages. Several modules call `logging.basicConfig(level=DEBUG)` at import time.
- **New routes:** put related endpoints in a module that exposes `router = APIRouter()` and include it in `main.py` with `app.include_router(...)`. Don't create more standalone `FastAPI()` apps. The existing ones in `ifttt_web_interface.py` and `ifttt_custom_call.py` are legacy or only used when running those files directly.
- **Serverless constraints:** don't add background threads, APScheduler jobs, or startup loops. Anything periodic must be an HTTP endpoint triggered by an external cron. The filesystem is read-only apart from bundled files.
- **Dependencies:** runtime dependencies go in `requirements.txt` (unpinned, and this is what Vercel installs). `requirements_test.txt` is a pinned snapshot of a developer environment, not a test-only list.

## Running locally

```bash
pip install -r requirements.txt
export postgres_host=... postgres_db=... postgres_port=5432 postgres_user=... postgres_password=...
export redis_host=... redis_port=... redis_username=... redis_password=...
export IFTTT_WEBHOOK=... MONGODB_CLOUD=...
python main.py                 # or: uvicorn main:app --reload --port 8000
python redis_update.py         # one-off Postgres -> Redis sync
python calenderview.py         # one-off Postgres -> MongoDB sync
```

Every module connects to Redis, Postgres, or MongoDB when it is used, and `redis_update.redis_client` is built at import time. As a result, importing `main` needs the Redis env vars to be present, although Redis doesn't have to be reachable until the first call.

## Testing

There is no automated test suite. If you add tests, use `pytest` with FastAPI's `TestClient`, and mock `requests.post`, `redis_client`, `psycopg2.connect`, `asyncpg.connect`, and `MongoClient`. Tests must never call the real IFTTT webhook.

## Known quirks (be aware; fix only when asked)

- `mongodb_fetch_calender_data` exists twice. The `calenderview.py` version returns `None` on error and converts `_id` to a string (JSON-safe). The `calenderly.py` version returns `[]` and leaves `ObjectId`s untouched.
- `ifttt_web_interface.py` uses misspelled constants (`POSTFRES_*`) that do map to the right env vars.
- `main.py` has an unused `get_db_connection()` plus unused imports, and `/status_code` returns the string `'200'`.
- `insert_ifttt_remainder` swallows DB errors and returns a message. The caller doesn't check the return value, so a failed insert still shows as "submitted".
- `make_iftttcall` has no request timeout (`ifttt_custom_call` uses `timeout=10`). Prefer adding a timeout in new HTTP calls.
