import logging
import os
from html import escape
from urllib.parse import quote

import httpx
from cache import get_cached
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions, Update
from telegram.error import NetworkError
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from sources.anilist import get_trending_anime
from sources.combined import gather_all_sources
from sources.youtube import get_trending_videos
from sources.google_trends import get_trending_searches
from sources.x_mock import XProvider

# Load configuration values from the local .env file.
load_dotenv()
x_provider = XProvider()


# Build the shared source menu used on the welcome and result messages.
def source_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Anime", callback_data="source:anime"),
                InlineKeyboardButton("YouTube", callback_data="source:youtube"),
            ],
            [
                InlineKeyboardButton("Google Trends", callback_data="source:google"),
                InlineKeyboardButton("X", callback_data="source:x"),
            ],
            [InlineKeyboardButton("All sources", callback_data="source:all")],
        ]
    )


# Welcome users and show the source menu.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        name = update.effective_user.first_name if update.effective_user else None
        name = name or "there"
        welcome = (
            f"Hi {name}! \U0001F44B\n"
            "See what's trending in Anime, YouTube, Google Trends, and X.\n"
            "Tap a button to explore. \u2728"
        )
        await update.message.reply_text(
            welcome,
            reply_markup=source_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


# Route source buttons to the existing command functions.
async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    # Answer every callback so Telegram stops the button loading spinner.
    await query.answer()
    if not query.message:
        return

    actions = {
        "source:all": trends,
        "source:anime": anime,
        "source:youtube": youtube,
        "source:google": google,
        "source:x": x_trends,
    }
    action = actions.get(query.data)
    if action:
        # Reuse each existing function and send its result as a new message.
        message_update = Update(update_id=update.update_id, message=query.message)
        await action(message_update, context)


# List the commands available in the bot.
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Choose a button under /start:\n"
            "Anime — top anime from AniList\n"
            "YouTube — popular videos in India\n"
            "Google Trends — trending searches in India\n"
            "X — sample trend data\n"
            "All sources — results from all four sources",
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )


# Log update failures on one short line without printing a traceback or secrets.
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    error = context.error
    error_name = type(error).__name__
    if isinstance(error, (NetworkError, httpx.HTTPError, TimeoutError)):
        logging.error("Network error: %s", error_name)
    else:
        logging.error("Bot error: %s", error_name)


# Fetch and display the current top five anime from AniList.
async def anime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    results = await get_cached("AniList", get_trending_anime)
    if isinstance(results, str):
        await update.message.reply_text(
            results,
            reply_markup=source_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    lines = ["<b>Trending anime</b>"]
    for number, item in enumerate(results, start=1):
        title = escape(item["title"])
        link = escape(item["link"], quote=True)
        score = item["score"]
        score_text = f"{score}/100" if score is not None else "Not rated"
        lines.append(f'{number}. <a href="{link}">{title}</a> | Score: {score_text}')

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=source_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# Fetch and display the current top five YouTube videos in India.
async def youtube(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    results = await get_cached("YouTube", get_trending_videos)
    if isinstance(results, str):
        await update.message.reply_text(
            results,
            reply_markup=source_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    lines = ["<b>Trending YouTube (Science &amp; Technology) in India</b>"]
    for number, item in enumerate(results, start=1):
        title = escape(item["title"])
        link = escape(item["link"], quote=True)
        channel = escape(item["channel"])
        views = f'{item["views"]:,}'
        lines.append(
            f'{number}. <a href="{link}">{title}</a> | {channel} | {views} views'
        )

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=source_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# Fetch and display the current top five Google searches in India.
async def google(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    results = await get_cached("Google Trends", get_trending_searches)
    if isinstance(results, str):
        await update.message.reply_text(
            results,
            reply_markup=source_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    lines = ["<b>Trending Google searches in India</b>"]
    for number, item in enumerate(results, start=1):
        term = escape(item["term"])
        link = escape(item["link"], quote=True)
        traffic = escape(item["traffic"])
        traffic_text = f" | {traffic}" if traffic else ""
        lines.append(f'{number}. <a href="{link}">{term}</a>{traffic_text}')

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=source_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# Display the sample top five X trends from the provider.
async def x_trends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    results = await get_cached("X", x_provider.get_trends)
    if isinstance(results, str):
        await update.message.reply_text(
            results,
            reply_markup=source_keyboard(),
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        return

    lines = ["<b>Trending on X in India</b>"]
    for number, item in enumerate(results, start=1):
        name = escape(item["title"])
        link = escape(item["link"], quote=True)
        extra = escape(item["extra"])
        lines.append(f'{number}. <a href="{link}">{name}</a> | {extra}')
    lines.append("Sample data (X API is paid)")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=source_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# Gather all four sources together and combine their results in one message.
async def trends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    results = await gather_all_sources(
        lambda: get_cached("AniList", get_trending_anime),
        lambda: get_cached("YouTube", get_trending_videos),
        lambda: get_cached("Google Trends", get_trending_searches),
        lambda: get_cached("X", x_provider.get_trends),
    )
    sections = [
        ("Anime", results[0], "title", "score"),
        ("YouTube (Science &amp; Technology)", results[1], "title", "channel"),
        ("Google Trends", results[2], "term", "traffic"),
        ("X", results[3], "title", "extra"),
    ]

    # Limit displayed text so even unusually long source data stays within Telegram's limit.
    def short_text(value: object, limit: int = 120) -> str:
        text = str(value)
        if len(text) > limit:
            text = text[: limit - 3] + "..."
        return escape(text)

    def render(max_items: int, compact: bool = False) -> str:
        label_limit = 20 if compact else 120
        message_lines = []
        for heading, result, label_key, detail_key in sections:
            message_lines.append(f"<b>{heading}</b>")
            if isinstance(result, BaseException):
                message_lines.append("Temporarily unavailable. Please try again later.")
                continue
            if isinstance(result, str):
                message_lines.append(short_text(result, 240))
                continue
            if not result:
                message_lines.append("No results are available right now.")
                continue

            for number, item in enumerate(result[:max_items], start=1):
                label = short_text(item[label_key], label_limit)
                raw_link = item["link"]
                if compact and heading == "Google Trends":
                    raw_link = f"https://www.google.com/search?q={quote(item['term'][:12])}"
                elif compact and heading == "X":
                    raw_link = f"https://x.com/search?q={quote(item['title'][:12])}"
                link = escape(raw_link, quote=True)
                line = f'{number}. <a href="{link}">{label}</a>'
                if heading == "Anime":
                    score = item["score"]
                    line += f" | Score: {score}/100" if score is not None else " | Not rated"
                elif heading.startswith("YouTube"):
                    detail_limit = 24 if compact else 80
                    line += f' | {short_text(item["channel"], detail_limit)} | {item["views"]:,} views'
                elif detail_key:
                    detail = item[detail_key]
                    if detail:
                        line += f" | {short_text(detail, 20 if compact else 60)}"
                message_lines.append(line)
            if heading == "X":
                message_lines.append("Sample data (X API is paid)")
        return "\n".join(message_lines)

    message = render(5)
    if len(message) > 4096:
        message = render(3)
    if len(message) > 4096:
        message = render(3, compact=True)
    await update.message.reply_text(
        message,
        parse_mode="HTML",
        reply_markup=source_keyboard(),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


# Read the bot token from the environment; never store it in the source code.
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is missing. Add it to your .env file.")

# Build the bot application and register the /start command.
app = Application.builder().token(token).build()
app.add_handler(CallbackQueryHandler(start_button))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_error_handler(error_handler)


# Start polling Telegram for updates when this file is run directly.
if __name__ == "__main__":
    app.run_polling()
