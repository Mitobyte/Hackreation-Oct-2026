#!/usr/bin/env python3
"""Turn a job posting (URL, saved .html, or .txt) into clean text for the helperize skill.

Usage:
  python3 fetch_posting.py <url | file.html | file.txt> [-o posting.txt]

- Prefers the schema.org JobPosting JSON-LD block that most job boards and
  company career pages embed (title, employer, location, pay, description).
- Falls back to the page's visible text.
- Standard library only, so it runs on a stock Mac.

Some boards (for example Indeed) block scripted requests. If you get a 403 or an
empty result, open the posting in a browser, save the page (File > Save As) or
copy the text into a .txt file, and pass that file instead.
"""
import argparse, html, json, re, sys, urllib.request
from html.parser import HTMLParser


class _Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "nav", "footer", "header"}
    BLOCK = {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "tr", "section"}

    def __init__(self):
        super().__init__()
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n")
        if tag == "li":
            self.out.append("- ")

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def visible_text(markup: str) -> str:
    p = _Text()
    p.feed(markup)
    text = html.unescape("".join(p.out))
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def job_posting_jsonld(markup: str):
    for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', markup, re.S | re.I):
        try:
            data = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item
    return None


def from_jsonld(jp: dict) -> str:
    org = jp.get("hiringOrganization") or {}
    loc = jp.get("jobLocation") or {}
    if isinstance(loc, list):
        loc = loc[0] if loc else {}
    addr = (loc.get("address") or {}) if isinstance(loc, dict) else {}
    pay = jp.get("baseSalary") or {}
    val = pay.get("value") or {} if isinstance(pay, dict) else {}
    lines = [
        f"Title: {jp.get('title', '')}",
        f"Employer: {org.get('name', '') if isinstance(org, dict) else org}",
        f"Location: {', '.join(str(addr.get(k, '')) for k in ('addressLocality', 'addressRegion') if addr.get(k))}",
        f"Employment type: {jp.get('employmentType', '')}",
        f"Pay: {val.get('minValue', val.get('value', ''))}-{val.get('maxValue', '')} {val.get('unitText', '')}".strip(" -"),
        "",
        visible_text(jp.get("description", "")),
    ]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    if a.source.startswith(("http://", "https://")):
        req = urllib.request.Request(a.source, headers={"User-Agent": "Mozilla/5.0 (helperize)"})
        try:
            markup = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        except Exception as e:  # noqa: BLE001
            sys.exit(f"Could not fetch ({e}). Save the page or paste its text into a .txt file and rerun.")
    else:
        markup = open(a.source, encoding="utf-8", errors="replace").read()

    if a.source.endswith(".txt"):
        text = markup.strip()
    else:
        jp = job_posting_jsonld(markup)
        text = from_jsonld(jp) if jp else visible_text(markup)

    if len(text) < 200:
        sys.exit("Very little text found. Save the full page or paste the posting text into a .txt file.")
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text + "\n")
    else:
        print(text)


if __name__ == "__main__":
    main()
