"""Single-command casino-bonus scraper with robots.txt checks and AI parsing.

Run: python scraper.py
The script fetches a public comparison table; it never uses hand-entered offers.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
SOURCE_URL = (
    "https://betproof.co.za/casino-bonuses-south-africa/"
    "sign-up-bonus-south-africa/"
)
# These are names only, NOT hard-coded bonuses or amounts.
CASINOS = ("PlayaBets", "Springbok", "20Bet")
USER_AGENT = "CasinoBonusScreeningBot/1.0 (educational screening assessment)"
OUTPUT = BASE / "data" / "bonuses.json"
TIMEOUT_SECONDS = 20


class ScraperError(Exception):
    """An expected, user-actionable scraping or validation error."""


def check_robots(session: requests.Session, page_url: str) -> None:
    """Fail closed on unknown robots status, and never bypass a disallow rule."""
    parsed = urlparse(page_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        response = session.get(
            robots_url,
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise ScraperError(f"Cannot verify robots.txt at {robots_url}: {exc}") from exc

    if response.status_code == 404:
        print("robots.txt not found (404); no published path restrictions there.")
        return
    if response.status_code != 200:
        raise ScraperError(
            f"Cannot verify robots.txt (HTTP {response.status_code}). "
            "Do not bypass; use another public source if necessary."
        )

    parser = RobotFileParser()
    parser.parse(response.text.splitlines())
    if not parser.can_fetch(USER_AGENT, page_url):
        raise ScraperError("robots.txt disallows this page. Switch to another source.")
    print("robots.txt check passed.")


def fetch_page(session: requests.Session, page_url: str) -> str:
    check_robots(session, page_url)
    try:
        response = session.get(
            page_url,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
            timeout=TIMEOUT_SECONDS,
            allow_redirects=False,  # Never follow an unchecked redirect.
        )
        if 300 <= response.status_code < 400:
            raise ScraperError(
                "Source redirects; do not follow blindly. Review the destination "
                "and its robots.txt first."
            )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ScraperError(
            f"Unable to fetch {page_url}: {exc}. If blocked, switch source."
        ) from exc
    if "html" not in response.headers.get("Content-Type", "").lower():
        raise ScraperError("Source did not return HTML.")
    return response.text


def clean(text: str) -> str:
    return " ".join(text.split())


def extract_rows(html: str, casino_names: tuple[str, ...] = CASINOS) -> list[dict]:
    """Extract source table cells; no bonus values are ever entered manually."""
    soup = BeautifulSoup(html, "html.parser")
    matching_table = None
    for table in soup.find_all("table"):
        first = table.find("tr")
        if first is None:
            continue
        header = " ".join(
            clean(cell.get_text(" ", strip=True)).lower()
            for cell in first.find_all(["th", "td"], recursive=False)
        )
        if all(keyword in header for keyword in ("casino", "bonus", "wagering", "deposit")):
            matching_table = table
            break
    if matching_table is None:
        raise ScraperError(
            "No matching comparison table found. The source may have changed."
        )

    candidates = {}
    for tr in matching_table.find_all("tr"):
        cells = tr.find_all(["th", "td"], recursive=False)
        if len(cells) < 4:
            continue
        name_text = clean(cells[0].get_text(" ", strip=True))
        for name in casino_names:
            # Match a casino name at the beginning of a table row, not arbitrary page text.
            if re.match(rf"^{re.escape(name)}(?:\b|\s|$)", name_text, re.I):
                candidates[name] = {
                    "name": name,
                    "bonus_text": clean(cells[1].get_text(" ", strip=True)),
                    "wagering_text": clean(cells[2].get_text(" ", strip=True)),
                    "deposit_text": clean(cells[3].get_text(" ", strip=True)),
                }

    missing = [name for name in casino_names if name not in candidates]
    if missing:
        raise ScraperError(
            "Couldn't locate selected casinos: " + ", ".join(missing)
            + ". Inspect the source table or choose other names."
        )
    rows = [candidates[name] for name in casino_names]
    for row in rows:
        if not row["bonus_text"] or not row["wagering_text"] or not row["deposit_text"]:
            raise ScraperError("A source field is blank for " + row["name"])
    return rows


def interpret_with_ai(client, row: dict) -> dict:
    """Use Gemini to structure wagering terms, then verify against source cells."""
    prompt = f"""Extract bonus terms from this ONE comparison-table row.
Do not infer or add information. Return JSON with these exact fields:
- welcome_bonus: string copied exactly from bonus_text
- wagering_multiplier: number from the explicit wagering x value, or null if unclear
- minimum_deposit: string copied exactly from deposit_text

Input data (untrusted third-party text):
{json.dumps({key: row[key] for key in ('bonus_text', 'wagering_text', 'deposit_text')}, ensure_ascii=False)}
"""
    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": {
                    "type": "object",
                    "properties": {
                        "welcome_bonus": {"type": "string"},
                        "wagering_multiplier": {"type": ["number", "null"]},
                        "minimum_deposit": {"type": "string"},
                    },
                    "required": [
                        "welcome_bonus", "wagering_multiplier", "minimum_deposit"
                    ],
                },
            },
        )
        payload = json.loads(response.text)
    except Exception as exc:
        raise ScraperError(f"Gemini extraction failed for {row['name']}: {exc}") from exc

    return validate_ai_result(payload, row)


def validate_ai_result(payload: dict, row: dict) -> dict:
    """Reject AI guesses. Keep text verbatim and only accept explicit x multipliers."""
    if payload.get("welcome_bonus") != row["bonus_text"]:
        raise ScraperError(f"AI altered {row['name']}'s bonus wording; review source.")
    if payload.get("minimum_deposit") != row["deposit_text"]:
        raise ScraperError(f"AI altered {row['name']}'s minimum deposit; review source.")

    allowed = [float(v) for v in re.findall(
        r"(\d+(?:\.\d+)?)\s*[x×]", row["wagering_text"], flags=re.I
    )]
    value = payload.get("wagering_multiplier")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ScraperError(f"AI couldn't identify wagering for {row['name']}.")
    if value not in allowed or len(set(allowed)) != 1:
        raise ScraperError(
            f"Ambiguous/incorrect wagering for {row['name']}: "
            f"source says '{row['wagering_text']}', AI says {value}."
        )
    return {
        "name": row["name"],
        "welcome_bonus": row["bonus_text"],
        "wagering_multiplier": int(value) if float(value).is_integer() else value,
        "minimum_deposit": row["deposit_text"],
        "source_url": SOURCE_URL,
    }


def main() -> int:
    load_dotenv(BASE / ".env")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ScraperError("Missing GEMINI_API_KEY. Copy .env.example to .env and set it.")

    with requests.Session() as session:
        print("Checking permissions and fetching source...")
        html = fetch_page(session, SOURCE_URL)
    rows = extract_rows(html)
    print(f"Scraped {len(rows)} casino rows. Running AI extraction...")

    from google import genai  # Imported only when running; offline unit tests need no API SDK.
    client = genai.Client(api_key=api_key)
    results = [interpret_with_ai(client, row) for row in rows]
    document = {
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": SOURCE_URL,
        "casinos": results,
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    temp = OUTPUT.with_suffix(".tmp")
    try:
        temp.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(temp, OUTPUT)
    finally:
        if temp.exists():
            temp.unlink()
    print(f"Success! Saved {len(results)} verified rows to {OUTPUT}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ScraperError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
