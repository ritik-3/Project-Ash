from __future__ import annotations

from pathlib import Path
from typing import Callable
from urllib.parse import quote_plus
import webbrowser

from project_ash.automation.strategies.common import retry_call
from project_ash.automation.strategies.gmail import (
    GMAIL_BODY_LOCATORS,
    GMAIL_COMPOSE_BUTTON_LOCATORS,
    GMAIL_RETRY_POLICY,
    GMAIL_SUBJECT_LOCATORS,
    GMAIL_TO_FIELD_LOCATORS,
)
from project_ash.automation.strategies.sheets import (
    SHEETS_FIRST_CELL_LOCATORS,
    SHEETS_RETRY_POLICY,
    SHEETS_TITLE_LOCATORS,
)
from project_ash.config import load_default_config


def _resolve_playwright_profile_dir() -> Path:
    cfg = load_default_config()
    profile = Path(cfg.playwright_user_data_dir)
    profile.mkdir(parents=True, exist_ok=True)
    return profile


def _run_with_persistent_page(start_url: str, workflow: Callable) -> str:
    cfg = load_default_config()
    profile_dir = _resolve_playwright_profile_dir()

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=cfg.playwright_headless,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.set_default_timeout(cfg.playwright_timeout_ms)
        page.goto(start_url, wait_until="domcontentloaded")
        return workflow(page)


def _first_visible_locator(page, selectors: list[str]):
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.count() > 0:
                return locator
        except Exception:
            continue
    return None


def open_website_with_playwright(url: str) -> str:
    target = url if url.startswith("http") else f"https://{url}"

    try:
        _run_with_persistent_page(target, lambda _page: "ok")
        return f"Opened website with Playwright: {target}"
    except Exception:
        webbrowser.open(target)
        return f"Opened website with fallback browser launcher: {target}"


def search_web_with_playwright(query: str) -> str:
    cleaned = query.strip() or ""
    target = f"https://www.google.com/search?q={cleaned.replace(' ', '+')}"

    try:
        _run_with_persistent_page(target, lambda _page: "ok")
        return f"Searched web with Playwright for: {cleaned or 'your request'}"
    except Exception:
        webbrowser.open(target)
        return f"Searching web with fallback browser launcher for: {cleaned or 'your request'}"


def draft_gmail_with_playwright(prompt: str, to: str | None = None) -> str:
    body = prompt.strip() or "Draft message"
    compose_url = "https://mail.google.com/mail/u/0/#inbox"

    try:
        def workflow(page):
            def action() -> str:
                compose_btn = _first_visible_locator(page, GMAIL_COMPOSE_BUTTON_LOCATORS)
                if compose_btn is None:
                    raise RuntimeError("Compose button not found")
                compose_btn.click()

                if to:
                    to_field = _first_visible_locator(page, GMAIL_TO_FIELD_LOCATORS)
                    if to_field is not None:
                        to_field.fill(to)

                subject = _first_visible_locator(page, GMAIL_SUBJECT_LOCATORS)
                if subject is not None:
                    subject.fill("Draft from Project Ash")

                body_field = _first_visible_locator(page, GMAIL_BODY_LOCATORS)
                if body_field is None:
                    raise RuntimeError("Message body field not found")
                body_field.fill(body)
                return "Opened Gmail compose and filled draft content using locator strategy."

            return retry_call(action, GMAIL_RETRY_POLICY)

        return _run_with_persistent_page(compose_url, workflow)
    except Exception:
        to_param = f"&to={quote_plus(to)}" if to else ""
        fallback_compose = (
            "https://mail.google.com/mail/?view=cm&fs=1&tf=1"
            f"{to_param}&su={quote_plus('Draft from Project Ash')}&body={quote_plus(body)}"
        )
        webbrowser.open(fallback_compose)
        return "Opened Gmail draft compose URL using fallback browser launcher."


def create_google_sheet_with_playwright(title: str) -> str:
    safe_title = title.strip() or "Untitled Sheet"
    start_url = "https://docs.google.com/spreadsheets/create"

    try:
        def workflow(page):
            def action() -> str:
                page.wait_for_timeout(SHEETS_RETRY_POLICY.wait_ms)
                title_input = _first_visible_locator(page, SHEETS_TITLE_LOCATORS)
                if title_input is None:
                    raise RuntimeError("Sheet title locator not found")
                title_input.click()
                title_input.fill(safe_title)
                page.keyboard.press("Enter")
                return f"Created Google Sheet and set title: {safe_title}"

            return retry_call(action, SHEETS_RETRY_POLICY)

        return _run_with_persistent_page(start_url, workflow)
    except Exception:
        webbrowser.open(start_url)
        return "Opened Google Sheets create page (fallback browser launcher)."


def add_google_sheet_row_with_playwright(row_text: str) -> str:
    payload = row_text.strip() or ""
    row_cells = [cell.strip() for cell in payload.split(",") if cell.strip()]
    typed_text = "\t".join(row_cells) if row_cells else payload
    start_url = "https://docs.google.com/spreadsheets"

    try:
        def workflow(page):
            def action() -> str:
                page.wait_for_timeout(SHEETS_RETRY_POLICY.wait_ms)
                first_cell = _first_visible_locator(page, SHEETS_FIRST_CELL_LOCATORS)
                if first_cell is None:
                    raise RuntimeError("Sheet cell locator not found")
                first_cell.click()
                if typed_text:
                    page.keyboard.type(typed_text)
                    page.keyboard.press("Enter")
                return "Added row data into active Google Sheet using retry+locator strategy."

            return retry_call(action, SHEETS_RETRY_POLICY)

        return _run_with_persistent_page(start_url, workflow)
    except Exception:
        webbrowser.open(start_url)
        return "Opened Google Sheets page. Please paste row manually if needed."
