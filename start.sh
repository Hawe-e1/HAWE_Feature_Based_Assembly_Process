#/bin/sh
uvicorn procgen.api:app --host 0.0.0.0 --port $PORT