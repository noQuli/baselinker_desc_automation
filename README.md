# baselinkier_automation

Automates BaseLinker product description updates by logging into the BaseLinker panel, reading product IDs from a CSV, generating polished Polish descriptions with AI, and saving the updated content back through Selenium. The workflow stores cookies for faster logins and records processed IDs.

## What it does
- Logs into BaseLinker using Selenium (cookies or credentials).
- Loads product IDs from `data/csv/numer_id.csv`.
- Generates new descriptions and benefits text via Perplexity/LangChain.
- Updates the main and secondary description fields.
- Writes progress to `data/csv/numer_id_recorded.csv`.

## Requirements
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or a compatible environment manager
- Firefox or Chrome WebDriver installed and on your PATH

## Setup
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Create a `.env` file with the required credentials and API key:
   ```bash
   EMAIL=you@example.com
   PASSWORD=your_password
   PPLX_API_KEY=your_perplexity_key
   ```
3. Provide the input CSV at `data/csv/numer_id.csv` with product IDs in the first column.

## Run
```bash
uv run run_code.py
```

## Configuration
`run_code.py` exposes a `WorkflowConfig` model for:
- `email`, `password`
- `username` (cookie namespace)
- `headless` (default `True`)
- `browser` (`firefox` or `chrome`)

Adjust these by editing `run_code.py` or wiring them into your own entry point.

## Data outputs
- Cookies: `data/cookies/{username}_pracuj_cookies.(pkl|json)`
- Processed IDs: `data/csv/numer_id_recorded.csv`

## Notes
- Make sure the WebDriver binary matches your browser version.
- The script opens the BaseLinker inventory URL for each product ID.
