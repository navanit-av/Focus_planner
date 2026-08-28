# Get Sh#t Done Planner v2

A redesigned Flask + SQLite weekly/daily task planner.

## Run

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

Open:

http://127.0.0.1:9744

The database is created automatically as `planner.db`.

## Existing database

If you already have the previous version's `planner.db` in the same folder, the app upgrades the weekly table automatically by adding the new priority field. Old time-block data is simply ignored; the Time Blocking feature is no longer exposed.
