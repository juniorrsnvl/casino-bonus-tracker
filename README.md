# CasinoTracker — AIBOOST Screening Assessment

A small full-stack exercise: scrape **3 casino bonus rows from one public comparison page**, use a Gemini language model to convert source text into structured fields, output JSON, and display it on a responsive webpage. No casino bonus amounts are hard-coded into the application.

## Technology

- **Python**, Requests, BeautifulSoup — one-page scraping and table extraction
- **Gemini 3.1 Flash-Lite** — converts the wagering text to a numeric multiplier (and copies the other fields)
- **JSON** — generated output, read by the frontend
- **HTML, CSS, JavaScript** — responsive webpage; no build step

## Setup (macOS / Linux)

Python 3.10+ is recommended.

```bash
cd casino-bonus-tracker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Get an API key at https://aistudio.google.com/apikey and edit `.env` to set `GEMINI_API_KEY` to your own key. **Never commit `.env`.** API availability and free-tier limits depend on the account and region.

## Run the scraper (one command)

```bash
python scraper.py
```

It checks the site's `robots.txt` **before** requesting its HTML, extracts three named rows, calls Gemini to structure their terms, verifies the model's output against the original source text, then atomically writes `data/bonuses.json`. If the source blocks access, disallows the path, changes layout, or AI returns ambiguous/incorrect values, the program stops without overwriting existing results. **Do not bypass a block.** Choose another public source if needed.

**Note:** `data/bonuses.json` is initially empty because the assessment explicitly forbids typing in bonus figures by hand. Run the scraper and commit the **real generated JSON** before publishing or submitting.

## View the website locally

From the project folder:

```bash
python -m http.server 8000
```

Open http://localhost:8000 in a browser. The page fetches `data/bonuses.json` and renders the three casino records on desktop or mobile. Do not open `index.html` directly as `file://`; browsers restrict file-based JSON fetching.

## Tests

```bash
python -m unittest discover -s tests -v
```

Tests use synthetic HTML fixtures to check parsing and AI-output validation; they **do not** claim to test actual live scraping.

## Publish (GitHub Pages, free)

1. After a successful scraper run, commit all files **except `.env` and `.venv`** to a public GitHub repository.
2. In the repository, open **Settings → Pages**.
3. Choose **Deploy from a branch → main → /(root)**, then save.
4. Wait for the Pages URL, test on desktop and mobile, and confirm that all three rows load and source links open.

## Output fields

Each row contains `name`, `welcome_bonus`, `wagering_multiplier`, `minimum_deposit`, and `source_url`. The root JSON object includes `updated_at` and `source` metadata.

## Limits and precautions

- Uses one comparison source, not official casino APIs. Offer details may be out of date; the site links to the source for verification.
- Runs only when commanded; it does **not** automatically update daily.
- `robots.txt` permission is checked at runtime. This project does not log in, evade CAPTCHAs, or work around blocks.
- Wagering descriptions with two different multipliers are rejected rather than guessed.
- The repository is educational, not an endorsement or gambling recommendation; 18+.
- Failed fetches, source markup changes, model/API limits, or unavailable robots rules may require switching sources and adapting the selector.

## Assessment deliverables

- [ ] Public GitHub Pages URL (after local successful run)
- [ ] Public GitHub repository containing this code AND generated JSON output
- [ ] Half-page scaling proposal (`PRODUCTION_PLAN.md`)
- [ ] Five-line note of the **actual** AI workflow, a **real** AI error and how it was caught (`SUBMISSION_NOTES.md`)
- [ ] Actual total time spent (stop after 3 hours)
