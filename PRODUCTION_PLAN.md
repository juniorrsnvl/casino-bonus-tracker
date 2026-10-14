# Scaling to 200 casinos — draft to review and put in my own words

For 200 casinos refreshed daily, I would run a Python scraping service on a small Linux VPS (for example DigitalOcean) rather than on a free static host. The VPS lets me control schedules, logging and request limits. I'd store verified bonus records in **PostgreSQL** with timestamps, source URLs and historical versions. A nightly `pg_dump` would be copied to separate object storage, with weekly restore checks. I'd only use sources that permit automated access and would implement rate limits and retries instead of bypassing site restrictions.

The frontend could stay a static site on **GitHub Pages or Cloudflare Pages**, while a small API on the VPS supplies current data. I'd buy a domain from a registrar (roughly $12–20/year), manage DNS in Cloudflare's free tier, and use **Let's Encrypt** for HTTPS. A daily cron job would run the scraper; logs, nonzero exit codes and a check-in monitor such as Healthchecks.io would alert me if it failed or no data changed. I'd preserve the last verified records and visibly mark stale data.

An initial budget might be **US$25–50/month**: VPS around $12–24, backups/storage around $3–6, domain around $1–2/month averaged, and a variable AI API allowance around $5–20. Actual costs would change with site complexity, request volume, and LLM usage.
