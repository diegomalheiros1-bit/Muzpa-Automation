# TrackHunter

TrackHunter is a Python + Playwright automation project for searching tracks on Muzpa, downloading MP3 files, and keeping an execution history to avoid duplicated downloads.

## What It Does

TrackHunter automates this workflow:

1. Opens Muzpa.
2. Logs in automatically or manually.
3. Reads a flexible `tracklist.txt`.
4. Searches one track at a time.
5. Clicks the best MP3 candidate found in the results.
6. Saves downloaded files in `downloads/`.
7. Writes a readable execution log in `logs/`.
8. Keeps a local history in `state/track_history.json`.

## Tech Stack

- Python 3.10+
- Playwright for Python
- Chromium browser automation

## Project Structure

```text
TrackHunter/
|- muzpa_bot.py      # CLI entrypoint and main orchestration
|- auth.py           # login and authentication flow
|- search.py         # search field detection and result matching
|- download.py       # per-track download workflow
|- report.py         # final TXT log generation
|- history.py        # local history for downloaded/missing tracks
|- utils.py          # text normalization, track parsing, helpers
|- models.py         # dataclasses used across modules
|- requirements.txt
|- tracklist.txt
|- downloads/        # downloaded MP3 files
|- logs/             # execution logs (.txt)
`- state/            # local history JSON
```

## Installation

```bash
pip install -r requirements.txt
playwright install chromium
```

## Tracklist

Edit `tracklist.txt` with one track per line:

```text
Kaskade & CID ft. Anabel Englund - Vision Blurred (Agents Of Time Remix)
Agents Of Time & Miss Monique - Rajada
Supermode - Tell Me Why
```

The tracklist is dynamic. You can add, remove, or replace tracks before each run.

## Automatic Login

Set credentials through environment variables:

```powershell
$env:MUZPA_EMAIL="your_email"
$env:MUZPA_PASSWORD="your_password"
python .\muzpa_bot.py --tracklist .\tracklist.txt --headless
```

## Manual Login

Use this mode when you want to log in through the browser window:

```powershell
python .\muzpa_bot.py --tracklist .\tracklist.txt --manual-login
```

## Useful Commands

Run with visible browser:

```powershell
python .\muzpa_bot.py --tracklist .\tracklist.txt
```

Run without browser UI:

```powershell
python .\muzpa_bot.py --tracklist .\tracklist.txt --headless
```

Force downloads even if tracks already exist in history:

```powershell
python .\muzpa_bot.py --tracklist .\tracklist.txt --force-download
```

Retry only tracks previously marked as missing:

```powershell
python .\muzpa_bot.py --retry-missing-only --headless
```

Use custom folders:

```powershell
python .\muzpa_bot.py --tracklist .\tracklist.txt --downloads .\downloads --logs .\logs --history .\state\track_history.json
```

## CLI Arguments

- `--tracklist`: path to the `.txt` file with tracks.
- `--downloads`: folder where MP3 files are saved.
- `--logs`: folder where execution logs are saved.
- `--history`: JSON file used as local execution history.
- `--output`: legacy alias for downloads folder.
- `--headless`: runs without browser UI.
- `--wait-login`: login timeout in milliseconds.
- `--manual-login`: disables automatic credential filling.
- `--force-download`: ignores history and downloads again.
- `--retry-missing-only`: runs only tracks stored as missing in history.

## Smart History

TrackHunter stores local state in:

```text
state/track_history.json
```

The history is used to:

- avoid downloading the same track repeatedly
- remember tracks that were not found
- retry missing tracks in future runs
- remove a track from missing once it is downloaded

Important behavior:

- A track is skipped only when it exists in history and its MP3 still exists in `downloads/`.
- If the MP3 was deleted from `downloads/`, TrackHunter downloads it again.
- Missing tracks stay eligible for future searches.
- `--force-download` bypasses the history.

## Search Strategy

For each track, TrackHunter tries:

1. Full query from `tracklist.txt`.
2. Fallback query using `title + version/remix`, without artist.

It prioritizes MP3 buttons, with ZIP/Download as fallback when needed.

## Log Format

Each run creates one TXT log:

```text
logs/log_execucao_YYYYMMDD_HHMMSS.txt
```

The log is organized into:

- `Resumo da execucao`
- `Concluidas com sucesso`
- `Ja baixadas / ignoradas`
- `Nao encontradas`
- `Erros`

## Runtime Files

These files/folders are local execution artifacts and are ignored by Git:

- `downloads/*`
- `logs/*.txt`
- `logs/*.csv`
- `state/*.json`
- `.env`

## Notes

- Do not hardcode credentials in the source code.
- Use environment variables for `MUZPA_EMAIL` and `MUZPA_PASSWORD`.
- Review the TXT log after each run to validate what was downloaded.
- Flexible matching can be useful for remixes and alternate versions, but the log should always be reviewed.

## Author

Project developed and evolved by Paulo as a real-world automation and portfolio project.

