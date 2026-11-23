#!/usr/bin/env python3
"""Fetch licensed photos from Wikimedia Commons for the 23 Nov 2026 entry.

Searches Commons for each target, takes the first result whose licence is
free (CC BY / CC BY-SA / public domain), downloads a 1200px-wide thumbnail,
and records title / licence / artist / URL in credits.json.
"""
import json
import os
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
UA = {"User-Agent": "makefun-entry-builder/1.0 (Seugii; contact: make.fun entry)"}

TARGETS = {
    "banner": "Mar-a-Lago",
    "kospi": "Korea Exchange",
    "nhs": "mammogram",
    "modi": "Narendra Modi",
    "vanuatu": "Vanuatu",
    "oil": "pumpjack",
    "fifa": "Wembley Stadium London",
}

def _licence_is_free(lic):
    norm = lic.lower().replace(" ", "").replace("-", "")
    return any(f in norm for f in ("ccby", "ccbysa", "cc0", "publicdomain"))


def api_search(query):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "6",
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|size|mime",
        "iiurlwidth": "1200",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pick_free(pages):
    """Return the first imageinfo whose licence looks free, else None."""
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        mime = info.get("mime", "")
        if not mime.startswith("image/") or mime == "image/svg+xml":
            continue
        meta = info.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "").lower()
        if _licence_is_free(lic):
            artist = (meta.get("Artist") or {}).get("value", "")
            return {
                "title": page.get("title", ""),
                "license": (meta.get("LicenseShortName") or {}).get("value", ""),
                "artist": artist,
                "url": info.get("thumburl") or info.get("url", ""),
                "width": info.get("thumbwidth"),
                "height": info.get("thumbheight"),
            }
    return None


def main():
    credits_path = os.path.join(OUT, "credits.json")
    credits = {}
    if os.path.exists(credits_path):
        credits = json.load(open(credits_path))
    # seed the two reused files with their known credits
    credits.setdefault("bitcoin", {
        "title": "File:Bitcoin BTC golden coin with the symbol.jpg",
        "license": "CC BY-SA 2.0",
        "artist": "Satheesh Sankaran",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e9/Bitcoin_BTC_golden_coin_with_the_symbol.jpg",
    })
    credits.setdefault("worldmap", {
        "title": "File:BlankMap-World.png",
        "license": "Public domain",
        "artist": "Vardion (public domain)",
        "url": "https://upload.wikimedia.org/wikipedia/commons/c/c3/BlankMap-World.png",
    })
    for key, query in TARGETS.items():
        dest = os.path.join(OUT, key + ".jpg")
        if os.path.exists(dest):
            print(f"{key}: already have {dest}, skip")
            continue
        data = api_search(query)
        pages = (data.get("query") or {}).get("pages") or {}
        chosen = pick_free(pages)
        if not chosen:
            print(f"{key}: NO free-licence result for {query!r}")
            continue
        req = urllib.request.Request(chosen["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        with open(dest, "wb") as f:
            f.write(blob)
        credits[key] = chosen
        print(f"{key}: {chosen['title']} | {chosen['license']} | {len(blob)} bytes")
    json.dump(credits, open(credits_path, "w"), indent=2, ensure_ascii=False)
    print("credits written to", credits_path)


if __name__ == "__main__":
    main()
