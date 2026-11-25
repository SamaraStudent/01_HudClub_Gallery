# HudClub Gallery Generator

A Python tool that parses Telegram chat JSON exports and generates a static HTML gallery with hashtag filtering.

## Features
- Parses Telegram chat exports (JSON).
- Collects photos by hashtags.
- Generates static HTML pages (Index, All Photos, User Pages).
- Interactive filtering by tags and "new" assignments.
- Built-in canvas for drawing/reviewing images directly in the browser.
- Modular architecture (Jinja2 templates, separated CSS/JS).

## Requirements
- Python 3.10+
- Install dependencies: `pip install -r requirements.txt`

## Usage
1. Configure your data paths in `config.py`.
2. Run the script:
   ```bash
   python run.py
