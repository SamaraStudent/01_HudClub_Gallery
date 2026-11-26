\# HudClub Gallery Project - Agent Guidelines



\## Project Overview

HudClub Gallery is a Python-based tool that parses Telegram chat JSON exports and generates a static HTML gallery. 

The project consists of two main parts:

1\. \*\*Editor (HudClub Gallery Admin)\*\*: A local web-based GUI built with `NiceGUI` for managing hashtags, configuring settings, and triggering site generation.

2\. \*\*Website (Site)\*\*: The final static HTML/CSS/JS output generated into the `Gallery\_Web` directory.



\## Tech Stack

\- Python 3.10+

\- \*\*NiceGUI\*\*: Used for the Editor interface.

\- \*\*Jinja2\*\*: Used for generating the final HTML website.

\- \*\*Vanilla JS \& CSS\*\*: Used for the frontend interactions of the Website (filters, drawing canvas, etc.).



\## Project Structure

\- `gui.py`: The main entry point for the Editor.

\- `ui/`: Contains modules for each tab in the Editor (`tab\_paths.py`, `tab\_generation.py`, `tab\_manager.py`, `tab\_themes.py`).

\- `core/`: Contains the core business logic.

&#x20; - `parser.py`: Parsing dates, hashtags, and user input.

&#x20; - `collector.py`: Parsing Telegram JSON files and collecting photos.

&#x20; - `renderer.py`: Jinja2 environment setup and page rendering.

&#x20; - `generator.py`: Orchestrates the generation process (combines collector and renderer).

&#x20; - `theme\_manager.py`: Handles saving/loading "skins" (themes).

&#x20; - `hashtag\_manager.py`: Handles loading/saving the hashtag database.

\- `templates/`: Jinja2 HTML templates for the Website.

\- `static/`: CSS and JS files for the Website.

\- `themes/`: Directory where design "skins" (snapshots of templates and static) are saved. `00\_undo` is reserved for rollback.

\- `config.py`: Global configuration and absolute paths.



\## Key Workflows

\- \*\*Run Editor\*\*: `python gui.py`

\- \*\*Generate Site\*\*: Handled by `core/generator.py::run\_generation()`. It cleans the `Gallery\_Web` folder, copies static files, collects photos based on active hashtags, and renders HTML files.

\- \*\*Theme Management\*\*: Handled by `core/theme\_manager.py`. Themes are copies of `templates/` and `static/`. 



\## Important Rules \& Gotchas

1\. \*\*Data is external\*\*: The actual data (JSON exports and `ListOfHashtags.json`) is NOT in this repository. Paths are defined in `config.py` and point to `D:\\PRJ\_Python\\00\_TelegaJSON\\02\_HudClub`.

2\. \*\*NiceGUI Checkboxes\*\*: NiceGUI/Quasar has issues with the `indeterminate` property for checkboxes. We use `ui.button` with icons (`check\_box`, `indeterminate\_check\_box`, `check\_box\_outline\_blank`) to simulate tri-state checkboxes in the Editor. Do not change this back to standard checkboxes.

3\. \*\*JS/CSS Scope\*\*: The CSS and JS in `static/` are meant for the \*generated Website\*, not the Editor. The Editor uses NiceGUI's built-in Tailwind CSS classes.

4\. \*\*Jinja2 Formatting\*\*: When editing HTML templates, ensure you use proper Jinja2 syntax (`{% for %}`, `{{ var }}`). Do not use Python's `.format()` syntax in these files.

5\. \*\*Hashtag JSON Structure\*\*: The `ListOfHashtags.json` uses a nested `links` dictionary (`{"links": {"telegram": "...", "boosty": "..."}}`). Always maintain this structure.

6\. \*\*Filters on the Website\*\*: The website filters use HTML `<details>` tags and vanilla JS in `static/js/filters.js`. Do not use external libraries for this unless requested.

