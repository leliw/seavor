#!/bin/sh

API_PORT=8080
PORT=4200

cd backend
PYTHONPATH="app" \
uv run uvicorn app.main:app --reload --port=$API_PORT &
UVICORN_PID=$!
cd ../frontend

if [ -f proxy-dev.conf.json ]; then
  rm proxy-dev.conf.json
fi

cat <<EOF >> proxy-dev.conf.json
{
   "/api": {
     "target": "http://localhost:$API_PORT",
     "secure": false
   }
 }
EOF

ng serve -o --proxy-config=proxy-dev.conf.json --port=$PORT

rm proxy-dev.conf.json

cd ..
kill $UVICORN_PID
