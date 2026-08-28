#!/bin/bash

PROJECT="$HOME/Focus_Planner"
PYTHON="$PROJECT/.venv/bin/python"
URL="http://127.0.0.1:9744"
PIDFILE="$PROJECT/server.pid"

cd "$PROJECT" || exit 1

# -------------------------
# STOP
# -------------------------
if [ "$1" = "stop" ]; then

    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")

        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping Focus Planner (PID $PID)..."
            kill "$PID"

            # Give Flask a moment to exit
            for i in {1..20}; do
                if ! kill -0 "$PID" 2>/dev/null; then
                    break
                fi
                sleep 0.1
            done
        fi

        rm -f "$PIDFILE"
    fi

    echo "Focus Planner stopped."
    exit 0
fi

# -------------------------
# RESTART
# -------------------------
if [ "$1" = "restart" ]; then
    "$0" stop
    sleep 0.5
fi

# -------------------------
# CHECK PID FILE
# -------------------------
if [ -f "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE")

    if kill -0 "$PID" 2>/dev/null; then
        open -na "Google Chrome" --args --app="$URL" --new-window
        exit 0
    fi

    rm -f "$PIDFILE"
fi

# -------------------------
# CHECK SERVER
# -------------------------
if curl -s "$URL" > /dev/null 2>&1; then
    open -na "Google Chrome" --args --app="$URL" --new-window
    exit 0
fi

# -------------------------
# START FLASK
# -------------------------
"$PYTHON" "$PROJECT/app.py" > "$PROJECT/server.log" 2>&1 &
SERVER_PID=$!

echo "$SERVER_PID" > "$PIDFILE"

# -------------------------
# WAIT FOR SERVER
# -------------------------
for i in {1..30}; do
    if curl -s "$URL" > /dev/null 2>&1; then
        break
    fi
    sleep 0.5
done

# -------------------------
# VERIFY SERVER
# -------------------------
if ! curl -s "$URL" > /dev/null 2>&1; then
    echo "Focus Planner failed to start."
    rm -f "$PIDFILE"
    exit 1
fi

# -------------------------
# OPEN CHROME
# -------------------------
open -na "Google Chrome" --args --app="$URL" --new-window

echo "Focus Planner running."
echo "PID: $SERVER_PID"
echo "URL: $URL"