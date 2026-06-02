# kArmas_SPiDeR2.0 🎩

pip install aiohttp beautifulsoup4 lxml

python kArmas_SPiDeR2.0.py https://example.com --max-depth 4 --concurrency 30

python kArmas_SPiDeR2.0.py https://target.com \
  --max-depth 5 \
  --max-pages 5000 \
  --concurrency 40 \
  --delay 0.1 \
  --output-dir ./results \
  --exclude-pattern "(logout|delete|admin)"


  kArmas_SPiDeR2.0 is locked and loaded. Here's what the beast does:
Core Engine
Fully async with aiohttp — up to 20 concurrent requests by default (configurable)
Async worker pool with live progress reporting every 5s
Graceful Ctrl+C interrupt — saves whatever it collected
Crawl Intelligence
BFS queue with configurable max depth and max pages
Scope control — stay on exact domain or allow all subdomains
robots.txt compliance (cached per domain, can be disabled)
URL deduplication, fragment stripping, and trailing-slash normalization
Include/exclude regex patterns
Asset filtering (skip JS/CSS/images unless you want them)
Data Extraction per page
Status code, content-type, load time, page size, SHA-256 hash
Title, meta description, H1 tags
Email addresses (regex harvested, globally deduplicated)
Phone numbers
All outbound links, images, form count, script count, word count
Redirect chain tracking
Output (4 files per run)
| File | Contents |
|---|---|
| *.json | Full structured data for every page |
| *.csv | Flat spreadsheet summary |
| *_sitemap.xml | Valid sitemap XML for all 200-OK pages |
| *_emails.txt | Deduplicated email harvest |
| *_links.txt | Clean list of all crawled URLs |
