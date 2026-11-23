#!/usr/bin/env python3
"""Fetch 4 more licensed photos for the ALSO ON promotions (revision round)."""
import json, os, urllib.parse, urllib.request
API = "https://commons.wikimedia.org/w/api.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos")
UA = {"User-Agent": "makefun-entry-builder/1.0 (Seugii; contact: make.fun entry)"}
TARGETS = {
    "msci": "National Monument Monas Jakarta",
    "korea": "Gwanghwamun Seoul",
    "india": "Bombay Stock Exchange Mumbai",
    "taiwan": "Taipei 101",
}
def licence_free(lic):
    n = lic.lower().replace(" ", "").replace("-", "")
    return any(f in n for f in ("ccby", "ccbysa", "cc0", "publicdomain"))
def api_search(q):
    p = {"action": "query", "format": "json", "generator": "search", "gsrsearch": q,
         "gsrnamespace": "6", "gsrlimit": "6", "prop": "imageinfo",
         "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "1200"}
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(p), headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
def pick(pages):
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        if not (info.get("mime", "").startswith("image/")) or info.get("mime") == "image/svg+xml":
            continue
        meta = info.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "")
        if licence_free(lic):
            return {"title": page.get("title", ""), "license": lic,
                    "artist": (meta.get("Artist") or {}).get("value", ""),
                    "url": info.get("thumburl") or info.get("url", ""),
                    "width": info.get("thumbwidth"), "height": info.get("thumbheight"),
                    "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page.get("title", "").replace(" ", "_"))}
    return None
def main():
    cp = os.path.join(OUT, "credits.json")
    credits = json.load(open(cp))
    for key, q in TARGETS.items():
        dest = os.path.join(OUT, key + ".jpg")
        if os.path.exists(dest):
            print(key, "already have", dest, "skip"); continue
        data = api_search(q)
        pages = (data.get("query") or {}).get("pages") or {}
        chosen = pick(pages)
        if not chosen:
            print(key, "NO free result for", repr(q)); continue
        req = urllib.request.Request(chosen["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            blob = r.read()
        open(dest, "wb").write(blob)
        credits[key] = chosen
        print(key, "->", chosen["title"], "|", chosen["license"], "|", len(blob), "bytes")
    json.dump(credits, open(cp, "w"), indent=2, ensure_ascii=False)
    print("credits updated")
if __name__ == "__main__":
    main()
