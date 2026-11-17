# Trend Radar: a Telegram bot that shows what is trending right now

Trend Radar brings current anime, video, search, and social trends into one Telegram chat.

## Description

This bot shows the top five results from AniList, YouTube, Google Trends, and X. Use an inline button to view one source or combine all four in one message.

I built Trend Radar as an assessment project to show trends from four sources in one place.

I chose `python-telegram-bot` for Telegram commands and buttons, `httpx` for asynchronous web requests, `cachetools` for a simple time-limited cache, `trendspyg` for Google Trends RSS data, and `pytest` for offline tests. `python-dotenv` loads private settings from `.env`.

Some challenges were that X's API requires paid credits, Google does not provide an official Trends API, and one failing source should not stop the others. I also run only one bot process at a time because two copies polling with the same Telegram token can conflict.

## Table of Contents

- [Description](#description)
- [Table of Contents](#table-of-contents)
- [Features](#features)
- [Installation](#installation)
- [How to use](#how-to-use)
- [How the code is organised](#how-the-code-is-organised)
- [How each source works](#how-each-source-works)
- [Replacing the X mock provider](#replacing-the-x-mock-provider)
- [Caching](#caching)
- [Tests](#tests)
- [Known limits](#known-limits)
- [What I would do next](#what-i-would-do-next)
- [AI tools used](#ai-tools-used)
- [Credits and references](#credits-and-references)
- [Security](#security)
- [License](#license)

## Features

- Inline buttons for Anime, YouTube, Google Trends, X, and All sources.
- Top-five lists with clickable links.
- All sources fetches the four providers concurrently.
- Five-minute caching for successful results.
- A failing source does not prevent the other sources from returning results.
- Friendly source errors and one-line logging for unexpected bot errors.
- Offline tests for caching, the X mock, and combined-source failures.
- Link previews are disabled in bot messages.

## Installation

### Requirements

- Python 3.10 or newer
- Git

### Steps

Clone the repository. Replace the example URL and folder name below with your repository URL and its folder name:

```powershell
git clone https://github.com/sivanijs/trend-radar-bot.git
cd trend-radar-bot```

Create and activate a virtual environment, install the requirements, and copy the example settings file:

```powershell
py 3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

### API keys

- **Telegram:** Message [@BotFather](https://t.me/BotFather), send `/newbot`, and follow the prompts to get a bot token. Add it to `TELEGRAM_BOT_TOKEN` in `.env`.
- **YouTube:** In the [Google Cloud Console](https://console.cloud.google.com/), create or select a project, enable [YouTube Data API v3](https://developers.google.com/youtube/v3/getting-started), and create an API key under APIs & Services > Credentials. Add it to `YOUTUBE_API_KEY` in `.env`.
- AniList and Google Trends need no key. X currently uses sample data and needs no key.

Run the bot with:

```powershell
python bot.py
```

## How to use

Send `/start` to see the welcome message and buttons:

- **Anime:** Show trending anime from AniList.
- **YouTube:** Show popular Science & Technology videos in India, with an unfiltered fallback if YouTube rejects that category.
- **Google Trends:** Show trending searches in India.
- **X:** Show sample X trends.
- **All sources:** Show results from all four sources together.

`/help` describes the buttons. Result messages keep the buttons underneath so you can choose another source.

### Screenshots

I will add screenshots to `docs/` later:

![Start menu placeholder](docs/start.png)

![All sources results placeholder](docs/all-sources.png)

## How the code is organised

```text
trend-pulse/
|-- bot.py
|-- cache.py
|-- sources/
|   |-- anilist.py
|   |-- combined.py
|   |-- google_trends.py
|   |-- x_mock.py
|   `-- youtube.py
|-- tests/
|   |-- test_cache.py
|   |-- test_combined.py
|   `-- test_x_mock.py
|-- requirements.txt
|-- .env.example
|-- .gitignore
|-- LICENSE
`-- README.md
```

- `bot.py` handles Telegram commands, buttons, messages, and errors.
- `cache.py` stores successful results temporarily.
- `sources/__init__.py` marks `sources/` as a Python package.
- `sources/anilist.py` fetches AniList data.
- `sources/youtube.py` fetches YouTube videos.
- `sources/google_trends.py` fetches Google Trends RSS data through `trendspyg`.
- `sources/x_mock.py` provides sample X trends.
- `sources/combined.py` gathers sources while preserving individual failures.
- `tests/test_cache.py`, `tests/test_combined.py`, and `tests/test_x_mock.py` contain offline tests.
- `requirements.txt` lists the required Python packages.
- `.env.example` shows placeholder settings for a private `.env` file.
- `.gitignore` excludes secrets, environments, and generated files.
- `LICENSE` contains the MIT license; `README.md` documents setup and use.

## How each source works

- **AniList:** `sources/anilist.py` sends a GraphQL request for the top five anime. It needs no API key.
- **YouTube:** `sources/youtube.py` calls YouTube Data API v3 `videos.list` with `chart=mostPopular`, requests the Science & Technology category (ID `28`), and falls back to no category if that request fails. Change `VIDEO_CATEGORY_ID` near the top of the file to select another category.
- **Google Trends:** `sources/google_trends.py` uses the unofficial `trendspyg` library in RSS mode for India. The blocking library call runs in a worker thread; no key or browser is needed.
- **X:** `sources/x_mock.py` returns five sample trends because the X API is paid.

## Replacing the X mock provider

The bot calls `XProvider.get_trends()` from `sources/x_mock.py`. A real provider can replace the implementation while keeping the same class name, file path, and method, so `bot.py` does not need to change. The real provider would read `X_BEARER_TOKEN` from `.env` and call the paid X API.

The method should keep returning a list with `title`, `extra`, and `link` fields:

```python
import os

class XProvider:
    async def get_trends(self):
        token = os.getenv("X_BEARER_TOKEN")  # Store the token in .env
        # Use token to request X trends, then map them into this structure.
        return [
            {"title": "Example trend", "extra": "12K posts", "link": "https://x.com/search?q=Example"}
        ]
```

## Caching

`cache.py` uses an in-memory five-minute TTL. Successful results are cached; error strings, empty results, and raised exceptions are not. The cache resets when the bot restarts.

## Tests

Run the offline test suite with:

```powershell
python -m pytest
```

The tests check that successful cache results are reused, error strings are retried, the X mock returns five complete items, and a failed source does not block the other fake sources. They do not use the internet or real keys.

## Known limits

- X results are sample data because the X API requires paid credits.
- `trendspyg` is unofficial and may change.
- The bot only runs while `python bot.py` is running on an internet-connected computer. Run one copy at a time with the same Telegram token.
- The in-memory cache resets on restart.
- YouTube API requests count against a daily quota.
- Link previews are off, though links remain clickable.

## What I would do next

- Add a real X provider.
- Use Redis or a database for shared, persistent caching.
- Deploy the bot online.
- Add more countries, more tests, and better filtering of YouTube content.

## AI tools used

- **OpenAI Codex (in VS Code):** used to generate and edit code
  from my prompts, including the bot, the four sources, caching
  and the tests.
- **Claude:** used for planning, step-by-step guidance, explaining
  errors.

I tested the bot myself by running it in Telegram, running the
tests, and fixing problems as they appeared. I also set up the
Telegram bot, the YouTube API key and the GitHub repository myself.

## Credits and references

- [python-telegram-bot documentation](https://docs.python-telegram-bot.org/en/v21.9/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [YouTube Data API `videos.list`](https://developers.google.com/youtube/v3/docs/videos/list)
- [AniList GraphQL API documentation](https://docs.anilist.co/guide/graphql/)
- [trendspyg on PyPI](https://pypi.org/project/trendspyg/)
- freeCodeCamp: [How to Write a Good README File for Your GitHub Project](https://www.freecodecamp.org/news/how-to-write-a-good-readme-file)

## Security

Keep API keys only in `.env`; Git ignores that file. Do not commit it. If a key is exposed, revoke or replace it straight away. `.env.example` contains placeholders only.

## License

This project is licensed under the MIT License. See the LICENSE file for details.