# Submission Notes — CasinoTracker

**Assessment:** AIBOOST Pty — Web Developer screening task  
**Date:** 14 October 2026

## Submission links

- **Live website:** https://juniorrsnvl.github.io/casino-bonus-tracker/
- **GitHub repository:** https://github.com/juniorrsnvl/casino-bonus-tracker
- **Generated data:** `data/bonuses.json` in the repository
- **Production scaling proposal:** `PRODUCTION_PLAN.md` in the repository

## What I built

I created a Python scraper that reads bonus terms for three casinos from a public comparison page, checks `robots.txt`, and uses the Gemini API to structure the extracted information. It validates the AI output against the text found on the source page and writes the results to a JSON file. I then built a responsive HTML, CSS, and JavaScript page that loads and displays that JSON. I tested the page on desktop and in Chrome's mobile device emulator and deployed it using GitHub Pages.

## Five lines about AI

1. I used ChatGPT to help scaffold the Python scraper, validation tests, and responsive webpage.
2. I used the Gemini API to convert the source's wagering text into a structured numeric multiplier.
3. One issue in the AI-assisted webpage implementation was that the original mobile layout clipped the logo and heading.
4. I caught it by testing the page in Chrome DevTools at phone-sized screen widths.
5. I adjusted the responsive CSS, refreshed the page, and checked that the header and casino cards fit the mobile screen.

## Time spent

- **Start:** 11:42 AM SAST (estimated)
- **Working site confirmed:** approximately 1:46 PM SAST
- **Elapsed by that check:** approximately 2 hours 4 minutes
- **Final total including documentation and submission:** *Update to the actual final duration before sending.*

## Limitations and next improvements

- The data comes from one third-party comparison page, so offers may change; the website links back to the source for verification.
- The scraper runs on demand rather than on a daily schedule. Automatic daily updates would be part of the production version.
- I would add monitoring, more source checks, and a database before scaling to 200 casinos.
- The website is an informational comparison demo, not a gambling recommendation.

**Note before submission:** Confirm the published site still loads all three records, verify the bonus figures against the linked source, and replace the final-duration placeholder with the actual time spent. The assessment's three-hour cap still applies.
]
