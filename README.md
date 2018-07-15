# Project_Mark
Temporarily I am putting things in `lib/` (to be renamed).

To run, add this directory to your `PYTHONPATH`, and try
```
python -m lib.hitbtc_ws --symbol TRXETH --log_path path/to/your/log.file
```

It will connect to hitbtc and log all the raw messages to your log file, with a rotation (every 100M of log will create a new file).
