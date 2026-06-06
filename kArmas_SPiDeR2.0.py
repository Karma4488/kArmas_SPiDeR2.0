#!/usr/bin/env python3
"""
██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ █████╗ ███████╗    ███████╗██████╗ ██╗██████╗ ███████╗██████╗
██║ ██╔╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝    ██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗
█████╔╝ ███████║██████╔╝██╔████╔██║███████║███████╗    ███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝
██╔═██╗ ██╔══██║██╔══██╗██║╚██╔╝██║██╔══██║╚════██║    ╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗
██║  ██╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║    ███████║██║     ██║██████╔╝███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝    ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
                                        v2.0  — by kArma
"""

import asyncio
import aiohttp
import argparse
import csv
import hashlib
import json
import logging
import os
import random
import re
import shutil
import sys
import time
import threading
import xml.etree.ElementTree as ET
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse, urldefrag, urlencode
from urllib.robotparser import RobotFileParser

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Missing dependency: pip install beautifulsoup4 aiohttp lxml")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
#  ANSI COLORS
# ─────────────────────────────────────────────────────────────────────────────
R  = "\033[91m"
G  = "\033[92m"
Y  = "\033[93m"
B  = "\033[94m"
M  = "\033[95m"
C  = "\033[96m"
W  = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"

# ─────────────────────────────────────────────────────────────────────────────
#  MATRIX RAIN
# ─────────────────────────────────────────────────────────────────────────────

MATRIX_CHARS = (
    "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789ABCDEF<>{}[]|/\\@#$%^&*~"
    "アイウエオカキクケコサシスセソタチツテトナニヌネノ"
)

BANNER_LINES = [
    r" ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ █████╗ ███████╗",
    r" ██║ ██╔╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝",
    r" █████╔╝ ███████║██████╔╝██╔████╔██║███████║███████╗",
    r" ██╔═██╗ ██╔══██║██╔══██╗██║╚██╔╝██║██╔══██║╚════██║",
    r" ██║  ██╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║",
    r" ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝",
    r" ███████╗██████╗ ██╗██████╗ ███████╗██████╗  ██████╗    ██████╗",
    r" ██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗╚════██╗  ██╔═████╗",
    r" ███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝ █████╔╝  ██║██╔██║",
    r" ╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗██╔═══╝   ████╔╝██║",
    r" ███████║██║     ██║██████╔╝███████╗██║  ██║███████╗  ╚██████╔╝",
    r" ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═════╝",
    r"",
    r"          ⟨ kArma's Spider 2.0 — The Strongest Crawler Ever ⟩",
    r"",
]

def _ansi_move(row: int, col: int) -> str:
    return f"\033[{row};{col}H"

def _ansi_color_green_bright() -> str:  return "\033[1;92m"
def _ansi_color_green_dim() -> str:     return "\033[2;32m"
def _ansi_color_green_mid() -> str:     return "\033[0;32m"
def _ansi_color_white() -> str:         return "\033[1;97m"
def _ansi_color_red_bold() -> str:      return "\033[1;91m"
def _ansi_color_yellow_bold() -> str:   return "\033[1;93m"
def _ansi_color_magenta_bold() -> str:  return "\033[1;95m"
def _ansi_color_reset() -> str:         return "\033[0m"
def _ansi_hide_cursor() -> str:         return "\033[?25l"
def _ansi_show_cursor() -> str:         return "\033[?25h"
def _ansi_clear_screen() -> str:        return "\033[2J"
def _ansi_alt_screen_on() -> str:       return "\033[?1049h"
def _ansi_alt_screen_off() -> str:      return "\033[?1049l"


def matrix_rain_intro(duration: float = 4.5, banner_reveal_at: float = 2.2):
    """
    Full-terminal matrix rain intro. Falls for `duration` seconds,
    then fades into the kArmas SPiDeR banner burned into the centre.
    """
    cols, rows = shutil.get_terminal_size(fallback=(100, 30))

    # ── state per column ─────────────────────────────────────────────────────
    class Drop:
        __slots__ = ("head", "length", "speed", "chars", "active")
        def __init__(self):
            self.head   = random.randint(-rows, 0)
            self.length = random.randint(6, rows // 2)
            self.speed  = random.choice([1, 1, 1, 2])
            self.chars  = [random.choice(MATRIX_CHARS) for _ in range(rows + 5)]
            self.active = True

        def step(self):
            self.head += self.speed
            # randomly mutate one char in the trail
            idx = random.randint(0, len(self.chars) - 1)
            self.chars[idx] = random.choice(MATRIX_CHARS)

    drops = [Drop() for _ in range(cols)]

    # ── banner geometry ───────────────────────────────────────────────────────
    banner_height = len(BANNER_LINES)
    banner_top    = max(1, (rows - banner_height) // 2)
    banner_width  = max((len(l) for l in BANNER_LINES), default=0)
    banner_left   = max(1, (cols - banner_width) // 2)

    out = sys.stdout
    out.write(_ansi_alt_screen_on())
    out.write(_ansi_hide_cursor())
    out.write(_ansi_clear_screen())
    out.flush()

    t_start   = time.perf_counter()
    revealed  = False
    frame_dt  = 0.045   # ~22 fps

    try:
        while True:
            now     = time.perf_counter()
            elapsed = now - t_start
            if elapsed >= duration:
                break

            buf = []

            # ── draw rain ────────────────────────────────────────────────────
            for col_idx, drop in enumerate(drops):
                drop.step()
                x = col_idx + 1   # 1-indexed terminal col

                for trail_pos in range(drop.length):
                    row_pos = drop.head - trail_pos
                    if row_pos < 1 or row_pos > rows:
                        continue

                    ch = drop.chars[row_pos % len(drop.chars)]

                    if trail_pos == 0:
                        color = _ansi_color_white()        # bright head
                    elif trail_pos < 3:
                        color = _ansi_color_green_bright()
                    elif trail_pos < drop.length // 2:
                        color = _ansi_color_green_mid()
                    else:
                        color = _ansi_color_green_dim()

                    buf.append(f"{_ansi_move(row_pos, x)}{color}{ch}")

                # erase tail cell
                tail = drop.head - drop.length
                if 1 <= tail <= rows:
                    buf.append(f"{_ansi_move(tail, x)} ")

                # recycle drop when it scrolls off
                if drop.head - drop.length > rows:
                    drops[col_idx] = Drop()
                    drops[col_idx].head = 0

            # ── reveal banner after threshold ─────────────────────────────────
            if elapsed >= banner_reveal_at and not revealed:
                revealed = True

            if revealed:
                fade = min(1.0, (elapsed - banner_reveal_at) / 1.5)
                for li, line in enumerate(BANNER_LINES):
                    r = banner_top + li
                    if r < 1 or r > rows:
                        continue
                    # choose colour by section
                    if li < 6:
                        col_code = _ansi_color_red_bold()
                    elif li < 12:
                        col_code = _ansi_color_magenta_bold()
                    elif "kArma" in line:
                        col_code = _ansi_color_yellow_bold()
                    else:
                        col_code = _ansi_color_green_mid()

                    # partial reveal: show chars left-to-right as fade increases
                    visible = int(len(line) * fade)
                    visible_line = line[:visible]

                    buf.append(
                        f"{_ansi_move(r, banner_left)}{col_code}{visible_line}"
                        f"{_ansi_color_reset()}"
                    )

            out.write("".join(buf) + _ansi_color_reset())
            out.flush()
            time.sleep(frame_dt)

        # ── hold final frame 0.4 s then fade out ─────────────────────────────
        time.sleep(0.4)

    finally:
        out.write(_ansi_show_cursor())
        out.write(_ansi_alt_screen_off())
        out.write(_ansi_color_reset())
        out.flush()

BANNER = f"""
{R}{BOLD}
 ██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ █████╗ ███████╗
 ██║ ██╔╝██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔════╝
 █████╔╝ ███████║██████╔╝██╔████╔██║███████║███████╗
 ██╔═██╗ ██╔══██║██╔══██╗██║╚██╔╝██║██╔══██║╚════██║
 ██║  ██╗██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║███████║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝{RESET}
{M}{BOLD} ███████╗██████╗ ██╗██████╗ ███████╗██████╗     ██████╗    ██████╗
 ██╔════╝██╔══██╗██║██╔══██╗██╔════╝██╔══██╗   ╚════██╗  ██╔═████╗
 ███████╗██████╔╝██║██║  ██║█████╗  ██████╔╝    █████╔╝  ██║██╔██║
 ╚════██║██╔═══╝ ██║██║  ██║██╔══╝  ██╔══██╗   ██╔═══╝   ████╔╝██║
 ███████║██║     ██║██████╔╝███████╗██║  ██║   ███████╗  ╚██████╔╝
 ╚══════╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚══════╝   ╚═════╝ {RESET}
{Y}                          ⟨ kArma's Spider 2.0 ⟩{RESET}
{DIM}            The strongest web crawler ever engineered{RESET}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PageResult:
    url: str
    status: int
    content_type: str
    title: str
    size_bytes: int
    load_time_ms: float
    links_found: int
    depth: int
    parent_url: str
    timestamp: str
    redirected_to: Optional[str] = None
    error: Optional[str] = None
    emails: list = field(default_factory=list)
    phones: list = field(default_factory=list)
    meta_description: str = ""
    h1_tags: list = field(default_factory=list)
    images: list = field(default_factory=list)
    forms: int = 0
    scripts: int = 0
    word_count: int = 0
    sha256: str = ""

@dataclass
class SpiderStats:
    start_time: float = field(default_factory=time.time)
    pages_crawled: int = 0
    pages_failed: int = 0
    pages_skipped: int = 0
    total_bytes: int = 0
    emails_found: set = field(default_factory=set)
    phones_found: set = field(default_factory=set)
    status_counts: dict = field(default_factory=lambda: defaultdict(int))
    content_types: dict = field(default_factory=lambda: defaultdict(int))
    deepest_url: tuple = ("", 0)  # (url, depth)

    @property
    def elapsed(self) -> float:
        return time.time() - self.start_time

    @property
    def pages_per_second(self) -> float:
        e = self.elapsed
        return round(self.pages_crawled / e, 2) if e > 0 else 0

# ─────────────────────────────────────────────────────────────────────────────
#  ROBOT PARSER CACHE
# ─────────────────────────────────────────────────────────────────────────────

class RobotsCache:
    def __init__(self):
        self._cache: dict[str, RobotFileParser] = {}

    async def is_allowed(self, url: str, user_agent: str, session: aiohttp.ClientSession, respect: bool) -> bool:
        if not respect:
            return True
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        if base not in self._cache:
            rp = RobotFileParser()
            robots_url = f"{base}/robots.txt"
            try:
                async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=5)) as r:
                    text = await r.text(errors="replace")
                rp.parse(text.splitlines())
            except Exception:
                rp.allow_all = True
            self._cache[base] = rp
        return self._cache[base].can_fetch(user_agent, url)

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN SPIDER CLASS
# ─────────────────────────────────────────────────────────────────────────────

class KArmasSpider:
    VERSION = "2.0"
    DEFAULT_UA = (
        "kArmas_SPiDeR/2.0 (+https://github.com/karmas/spider; "
        "educational-crawler)"
    )

    def __init__(self, cfg: argparse.Namespace):
        self.cfg = cfg
        self.stats = SpiderStats()
        self.robots = RobotsCache()

        self.visited: set[str] = set()
        self.queue: deque[tuple[str, int, str]] = deque()  # (url, depth, parent)
        self.results: list[PageResult] = []

        self._output_dir = Path(cfg.output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        self._setup_logging()
        self._semaphore: asyncio.Semaphore = None  # set in run()

    # ── logging ──────────────────────────────────────────────────────────────

    def _setup_logging(self):
        level = logging.DEBUG if self.cfg.verbose else logging.INFO
        fmt = "%(asctime)s %(levelname)-8s %(message)s"
        logging.basicConfig(level=level, format=fmt,
                            handlers=[
                                logging.StreamHandler(sys.stdout),
                                logging.FileHandler(
                                    self._output_dir / "spider.log", encoding="utf-8")
                            ])
        self.log = logging.getLogger("kArmasSpider")

    # ── URL helpers ───────────────────────────────────────────────────────────

    @staticmethod
    def _normalize(url: str) -> str:
        url, _ = urldefrag(url)          # strip fragment
        return url.rstrip("/") + "/"    # trailing-slash normalisation

    def _in_scope(self, url: str) -> bool:
        p = urlparse(url)
        seed = urlparse(self.cfg.url)
        if self.cfg.stay_on_domain:
            return p.netloc == seed.netloc
        if self.cfg.stay_on_subdomain:
            root = ".".join(seed.netloc.split(".")[-2:])
            return p.netloc.endswith(root)
        return True

    def _filter_url(self, url: str) -> bool:
        """Return True if URL should be crawled."""
        p = urlparse(url)
        if p.scheme not in ("http", "https"):
            return False
        if any(url.lower().endswith(ext) for ext in (
            ".pdf", ".zip", ".tar", ".gz", ".exe", ".dmg",
            ".mp4", ".mp3", ".avi", ".mov", ".jpg", ".jpeg",
            ".png", ".gif", ".svg", ".ico", ".woff", ".woff2",
            ".ttf", ".eot", ".css", ".js",
        )):
            if not self.cfg.crawl_assets:
                return False
        if self.cfg.exclude_pattern and re.search(self.cfg.exclude_pattern, url):
            return False
        if self.cfg.include_pattern and not re.search(self.cfg.include_pattern, url):
            return False
        return self._in_scope(url)

    # ── page fetching ─────────────────────────────────────────────────────────

    async def _fetch(self, url: str, depth: int, parent: str,
                     session: aiohttp.ClientSession) -> Optional[PageResult]:

        allowed = await self.robots.is_allowed(url, self.DEFAULT_UA, session,
                                                self.cfg.respect_robots)
        if not allowed:
            self.log.debug(f"[robots] blocked: {url}")
            self.stats.pages_skipped += 1
            return None

        headers = {"User-Agent": self.cfg.user_agent or self.DEFAULT_UA}
        t0 = time.perf_counter()
        try:
            async with session.get(
                url, headers=headers,
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=self.cfg.timeout),
                ssl=not self.cfg.no_ssl_verify,
            ) as resp:
                load_ms = round((time.perf_counter() - t0) * 1000, 1)
                raw = await resp.read()
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                final_url = str(resp.url)
                redirect_url = final_url if final_url != url else None

        except asyncio.TimeoutError:
            self.stats.pages_failed += 1
            self.log.warning(f"[timeout] {url}")
            return PageResult(url, 0, "", "", 0, 0, 0, depth, parent,
                              datetime.utcnow().isoformat(), error="Timeout")
        except Exception as e:
            self.stats.pages_failed += 1
            self.log.warning(f"[error] {url} — {e}")
            return PageResult(url, 0, "", "", 0, 0, 0, depth, parent,
                              datetime.utcnow().isoformat(), error=str(e))

        # track stats
        self.stats.status_counts[status] += 1
        self.stats.total_bytes += len(raw)
        ctype_key = content_type.split(";")[0].strip()
        self.stats.content_types[ctype_key] += 1

        # parse HTML
        links_found = 0
        title = meta_desc = ""
        emails = phones = h1s = images_list = []
        forms = scripts = word_count = 0
        new_urls: list[str] = []

        if "html" in content_type:
            try:
                text = raw.decode("utf-8", errors="replace")
                soup = BeautifulSoup(text, "lxml")
            except Exception:
                soup = None

            if soup:
                # title
                title_tag = soup.find("title")
                title = title_tag.get_text(strip=True) if title_tag else ""

                # meta description
                meta = soup.find("meta", attrs={"name": re.compile("description", re.I)})
                meta_desc = meta.get("content", "") if meta else ""

                # h1
                h1s = [t.get_text(strip=True) for t in soup.find_all("h1")][:5]

                # emails
                email_re = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
                emails = list(set(email_re.findall(text)))
                self.stats.emails_found.update(emails)

                # phones
                phone_re = re.compile(
                    r"(?:\+?\d{1,3}[\s\-.]?)?\(?\d{2,4}\)?[\s\-.]?\d{3,4}[\s\-.]?\d{3,4}"
                )
                phones = list(set(phone_re.findall(text)))[:20]
                self.stats.phones_found.update(phones)

                # images
                images_list = [
                    urljoin(url, img.get("src", ""))
                    for img in soup.find_all("img", src=True)
                ][:50]

                # forms & scripts
                forms = len(soup.find_all("form"))
                scripts = len(soup.find_all("script"))

                # word count (body text)
                body = soup.get_text(separator=" ")
                word_count = len(body.split())

                # extract links
                for tag in soup.find_all("a", href=True):
                    href = tag["href"].strip()
                    full = urljoin(url, href)
                    full = self._normalize(full)
                    if self._filter_url(full) and full not in self.visited:
                        new_urls.append(full)
                links_found = len(new_urls)

        sha = hashlib.sha256(raw).hexdigest()

        result = PageResult(
            url=url,
            status=status,
            content_type=content_type,
            title=title,
            size_bytes=len(raw),
            load_time_ms=load_ms,
            links_found=links_found,
            depth=depth,
            parent_url=parent,
            timestamp=datetime.utcnow().isoformat(),
            redirected_to=redirect_url,
            emails=emails,
            phones=phones,
            meta_description=meta_desc,
            h1_tags=h1s,
            images=images_list,
            forms=forms,
            scripts=scripts,
            word_count=word_count,
            sha256=sha,
        )

        # depth tracking
        if depth > self.stats.deepest_url[1]:
            self.stats.deepest_url = (url, depth)

        # enqueue discovered URLs
        if depth < self.cfg.max_depth:
            for new_url in new_urls:
                if new_url not in self.visited:
                    self.queue.append((new_url, depth + 1, url))

        return result

    # ── worker ────────────────────────────────────────────────────────────────

    async def _worker(self, session: aiohttp.ClientSession):
        while True:
            async with self._semaphore:
                if not self.queue:
                    await asyncio.sleep(0.05)
                    continue

                try:
                    url, depth, parent = self.queue.popleft()
                except IndexError:
                    await asyncio.sleep(0.05)
                    continue

                if url in self.visited:
                    continue
                if self.cfg.max_pages and self.stats.pages_crawled >= self.cfg.max_pages:
                    return

                self.visited.add(url)
                result = await self._fetch(url, depth, parent, session)
                if result:
                    self.results.append(result)
                    if result.error is None:
                        self.stats.pages_crawled += 1
                        color = G if result.status == 200 else (Y if result.status < 400 else R)
                        print(
                            f"{color}[{result.status}]{RESET} "
                            f"{DIM}d={depth}{RESET} "
                            f"{C}{result.load_time_ms:>7.1f}ms{RESET} "
                            f"{result.url[:90]}"
                        )
                    if self.cfg.delay:
                        await asyncio.sleep(self.cfg.delay)

    # ── run ───────────────────────────────────────────────────────────────────

    async def run(self):
        print(BANNER)
        seed = self._normalize(self.cfg.url)
        self.queue.append((seed, 0, ""))
        self._semaphore = asyncio.Semaphore(self.cfg.concurrency)

        connector = aiohttp.TCPConnector(
            limit=self.cfg.concurrency * 2,
            ssl=not self.cfg.no_ssl_verify,
        )
        async with aiohttp.ClientSession(connector=connector) as session:
            # spin up workers
            workers = [
                asyncio.create_task(self._worker(session))
                for _ in range(self.cfg.concurrency)
            ]

            # progress reporter
            async def _progress():
                while True:
                    await asyncio.sleep(5)
                    print(
                        f"{M}  ↻ crawled={self.stats.pages_crawled} "
                        f"queued={len(self.queue)} "
                        f"failed={self.stats.pages_failed} "
                        f"speed={self.stats.pages_per_second}p/s "
                        f"elapsed={self.stats.elapsed:.0f}s{RESET}"
                    )

            progress_task = asyncio.create_task(_progress())

            # wait until queue drained or limit hit
            while self.queue or any(not t.done() for t in workers):
                await asyncio.sleep(0.25)
                if not self.queue:
                    break
                if self.cfg.max_pages and self.stats.pages_crawled >= self.cfg.max_pages:
                    break

            for w in workers:
                w.cancel()
            progress_task.cancel()

        self._save_results()
        self._print_summary()

    # ── output ────────────────────────────────────────────────────────────────

    def _save_results(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = self._output_dir / f"karmas_spider_{ts}"

        # JSON (full)
        json_path = base.with_suffix(".json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.results], f, indent=2, default=str)
        self.log.info(f"[saved] JSON  → {json_path}")

        # CSV (flat summary)
        csv_path = base.with_suffix(".csv")
        csv_fields = [
            "url", "status", "title", "depth", "size_bytes",
            "load_time_ms", "links_found", "forms", "scripts",
            "word_count", "meta_description", "parent_url",
            "redirected_to", "content_type", "timestamp", "error", "sha256"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
            w.writeheader()
            for r in self.results:
                row = asdict(r)
                w.writerow(row)
        self.log.info(f"[saved] CSV   → {csv_path}")

        # Sitemap XML
        xml_path = base.with_name(base.name + "_sitemap.xml")
        root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        for r in self.results:
            if r.status == 200:
                url_el = ET.SubElement(root, "url")
                ET.SubElement(url_el, "loc").text = r.url
                ET.SubElement(url_el, "lastmod").text = r.timestamp[:10]
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(str(xml_path), encoding="unicode", xml_declaration=True)
        self.log.info(f"[saved] XML   → {xml_path}")

        # Emails list
        if self.stats.emails_found:
            em_path = base.with_name(base.name + "_emails.txt")
            em_path.write_text("\n".join(sorted(self.stats.emails_found)), encoding="utf-8")
            self.log.info(f"[saved] EMAILS→ {em_path}")

        # All links (plain text)
        links_path = base.with_name(base.name + "_links.txt")
        links_path.write_text(
            "\n".join(r.url for r in self.results if r.error is None),
            encoding="utf-8"
        )
        self.log.info(f"[saved] LINKS → {links_path}")

    def _print_summary(self):
        e = self.stats.elapsed
        print(f"""
{BOLD}{Y}╔══════════════════════════════════════════════╗
║          kArmas_SPiDeR 2.0  — DONE           ║
╚══════════════════════════════════════════════╝{RESET}

  {G}Pages crawled   : {self.stats.pages_crawled}
  {R}Pages failed    : {self.stats.pages_failed}
  {Y}Pages skipped   : {self.stats.pages_skipped}
  {C}Data downloaded : {self.stats.total_bytes / 1024:.1f} KB
  {M}Speed           : {self.stats.pages_per_second} pages/s
  {B}Elapsed time    : {e:.1f}s{RESET}

  {G}Emails found    : {len(self.stats.emails_found)}
  {Y}Phones found    : {len(self.stats.phones_found)}
  {C}Deepest URL     : d={self.stats.deepest_url[1]}  {self.stats.deepest_url[0][:60]}

  {DIM}HTTP status breakdown:{RESET}
""")
        for code, count in sorted(self.stats.status_counts.items()):
            bar = "█" * min(count, 50)
            col = G if code == 200 else (Y if code < 400 else R)
            print(f"    {col}{code}{RESET}  {bar} {count}")
        print()

# ─────────────────────────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kArmas_SPiDeR2.0",
        description="The strongest web crawler ever built.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    p.add_argument("url", help="Seed URL to start crawling from")

    # scope
    scope = p.add_argument_group("Scope")
    scope.add_argument("--max-depth", type=int, default=3,
                       help="Maximum crawl depth from seed")
    scope.add_argument("--max-pages", type=int, default=0,
                       help="Maximum number of pages to crawl (0 = unlimited)")
    scope.add_argument("--stay-on-domain", action="store_true", default=True,
                       help="Stay on the same domain as the seed URL")
    scope.add_argument("--stay-on-subdomain", action="store_true",
                       help="Allow all subdomains of the seed's root domain")
    scope.add_argument("--include-pattern", default="",
                       help="Regex: only crawl URLs matching this pattern")
    scope.add_argument("--exclude-pattern", default="",
                       help="Regex: skip URLs matching this pattern")
    scope.add_argument("--crawl-assets", action="store_true",
                       help="Also crawl CSS/JS/image URLs")

    # performance
    perf = p.add_argument_group("Performance")
    perf.add_argument("--concurrency", "-c", type=int, default=20,
                      help="Number of concurrent async requests")
    perf.add_argument("--timeout", type=float, default=10.0,
                      help="Per-request timeout in seconds")
    perf.add_argument("--delay", type=float, default=0.0,
                      help="Politeness delay (seconds) between requests per worker")

    # identity
    ident = p.add_argument_group("Identity")
    ident.add_argument("--user-agent", default="",
                       help="Custom User-Agent string (default: kArmas_SPiDeR/2.0)")
    ident.add_argument("--no-ssl-verify", action="store_true",
                       help="Disable SSL certificate verification")
    ident.add_argument("--respect-robots", action="store_true", default=True,
                       help="Respect robots.txt rules")
    ident.add_argument("--no-robots", dest="respect_robots", action="store_false",
                       help="Ignore robots.txt")

    # output
    out = p.add_argument_group("Output")
    out.add_argument("--output-dir", "-o", default="spider_output",
                     help="Directory to save results (JSON, CSV, XML, emails, links)")
    out.add_argument("--verbose", "-v", action="store_true",
                     help="Enable verbose/debug logging")
    out.add_argument("--no-intro", action="store_true",
                     help="Skip the matrix rain intro animation")

    return p


def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    cfg = parser.parse_args()

    # validate URL
    p = urlparse(cfg.url)
    if not p.scheme or not p.netloc:
        print(f"{R}[!] Invalid seed URL: {cfg.url}{RESET}")
        sys.exit(1)
    if p.scheme not in ("http", "https"):
        print(f"{R}[!] Only http/https URLs supported.{RESET}")
        sys.exit(1)

    # ── matrix rain intro ────────────────────────────────────────────────────
    if sys.stdout.isatty() and not cfg.no_intro:
        try:
            matrix_rain_intro(duration=4.8, banner_reveal_at=2.0)
        except Exception:
            pass   # never let the intro crash the actual crawl

    spider = KArmasSpider(cfg)
    try:
        asyncio.run(spider.run())
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Interrupted by user.{RESET}")
        spider._save_results()
        spider._print_summary()


if __name__ == "__main__":
    main()

