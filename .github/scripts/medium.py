"""Rewrites the README's latest-posts list from the Medium RSS feed. Leaves the README alone when the fetch fails."""

import html
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit

FEED = "https://medium.com/feed/@kushalbanda"
README = Path(__file__).resolve().parents[2] / "README.md"
LIMIT = 5

PUBLICATIONS = {
    "pub.towardsai.net": "Towards AI",
    "generativeai.pub": "Generative AI",
    "aws.plainenglish.io": "AWS in Plain English",
    "design-bootcamp": "Bootcamp",
    "write-a-catalyst": "Write A Catalyst",
}


def publication(url: str) -> str:
    parts = urlsplit(url)
    if parts.hostname != "medium.com":
        return PUBLICATIONS.get(parts.hostname or "", parts.hostname or "Medium")
    first = parts.path.split("/")[1] if "/" in parts.path else ""
    return "Medium" if first.startswith("@") else PUBLICATIONS.get(first, "Medium")


def main() -> int:
    req = urllib.request.Request(FEED, headers={"user-agent": "github.com/kushalBanda profile README"})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            root = ET.fromstring(res.read())
    except Exception as err:  # Medium blocks some CI hosts now and then; keep yesterday's list.
        print(f"medium: feed unavailable, README unchanged ({err})")
        return 0

    lines = []
    for item in root.iter("item"):
        title, link, date = item.findtext("title"), item.findtext("link"), item.findtext("pubDate")
        if not (title and link and date):
            continue
        url = link.split("?")[0]
        day = parsedate_to_datetime(date).strftime("%-d %b %Y")
        safe = html.unescape(title).strip().replace("[", "\\[").replace("]", "\\]")
        lines.append(f"- [{safe}]({url})<br><sub>{publication(url)} · {day}</sub>")
        if len(lines) == LIMIT:
            break
    if not lines:
        print("medium: feed had no posts, README unchanged")
        return 0

    text = README.read_text()
    block = "<!-- medium:start -->\n" + "\n".join(lines) + "\n<!-- medium:end -->"
    new = re.sub(r"<!-- medium:start -->.*?<!-- medium:end -->", lambda _: block, text, flags=re.S)
    if new != text:
        README.write_text(new)
        print(f"medium: wrote {len(lines)} posts")
    else:
        print("medium: no change")
    return 0


if __name__ == "__main__":
    sys.exit(main())
