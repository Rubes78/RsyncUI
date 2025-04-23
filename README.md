# Rsync Web GUI

A Flask-based interface for selecting source and destination folders for rsync backup operations.

## Features
- Browse the local file system via web interface
- Select source and destination paths using folder picker
- Ready for rsync command integration and Docker packaging

## Setup
```bash
pip install flask
python rsync_web_browser.py
```

Then visit: [http://localhost:5055](http://localhost:5055)

## To Do
- Add rsync execution logic
- Add logging toggle and output viewer
- Docker packaging
