"""
Scraping Jurnal Akademik — CrossRef REST API (Fixed)
Optimized with Polite Pool & polite headers
Output: raw_json/crossref.json and csv/crossref.csv
"""
import json
import csv
import os
import time
import urllib.request
import urllib.parse
import urllib.error
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "raw_json")
CSV_DIR = os.path.join(BASE_DIR, "csv")
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

SEARCH_DATE = datetime.now().strftime("%Y-%m-%d")
CONTACT_EMAIL = "arya.refman.academic@gmail.com"

CSV_HEADERS = [
    "Article_ID", "Source_Type", "Database/Source", "Search_Date",
    "Search_Query", "Title", "Authors", "Year", "Journal/Conference",
    "DOI", "URL", "Abstract", "Document_Type", "Language",
    "Duplicate_Key", "Duplicate?", "Notes"
]

def http_get(url, retries=4, base_delay=2.0):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", f"AcademicSLR/1.0 (mailto:{CONTACT_EMAIL})")
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = base_delay * (2 ** (attempt + 1))
                print(f"    [Rate Limit 429] Waiting {wait:.1f}s before retry...", flush=True)
                time.sleep(wait)
            elif e.code in (500, 502, 503, 504):
                wait = base_delay * (attempt + 1)
                print(f"    [Server Error {e.code}] Waiting {wait:.1f}s...", flush=True)
                time.sleep(wait)
            else:
                print(f"    [HTTP Error {e.code}] {e.reason}", flush=True)
                return None
        except Exception as e:
            print(f"    [Attempt {attempt+1} Error] {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(base_delay * (attempt + 1))
    return None

def make_duplicate_key(title, year):
    if not title:
        return ""
    clean = title.lower().strip()
    for ch in ".:;,!?'\"()[]{}-_/":
        clean = clean.replace(ch, " ")
    words = [w for w in clean.split() if w][:8]
    return f"{'_'.join(words)}_{year}" if year else '_'.join(words)

def search_crossref():
    print("=" * 60, flush=True)
    print("SCRAPING CROSSREF API (Polite Pool)", flush=True)
    print("=" * 60, flush=True)

    all_items = []
    seen_dois = set()
    seen_titles = set()

    # Queries aligned with PICOC / Search Strategy in Excel
    cr_queries = [
        ("Q01", "world model JEPA video prediction"),
        ("Q02", "joint embedding predictive architecture video"),
        ("Q03", "world model generative video diffusion"),
        ("Q04", "V-JEPA video representation self-supervised"),
        ("Q05", "generative world model reinforcement learning"),
        ("Q06", "latent dynamics model video prediction"),
        ("Q07", "video world model visual planning simulation"),
        ("Q08", "I-JEPA joint embedding predictive architecture"),
        ("Q09", "autoregressive world model video generation"),
        ("Q10", "diffusion world model interactive simulation"),
        ("Q11", "learned dynamics model video reinforcement learning"),
        ("Q12", "action-conditioned video prediction world model"),
        ("Q13", "hierarchical JEPA planning robotics"),
        ("Q14", "spatiotemporal world model video forecasting"),
    ]

    for qid, query in cr_queries:
        print(f"\n[{qid}] Query: '{query}'", flush=True)
        offset = 0
        query_added = 0
        max_per_query = 100  # Up to 2 pages of 50 = 100 items per query

        while offset < max_per_query:
            params = urllib.parse.urlencode({
                "query": query,
                "filter": "from-pub-date:2018-01-01,until-pub-date:2026-12-31,type:journal-article",
                "rows": 50,
                "offset": offset,
                "mailto": CONTACT_EMAIL
            })
            url = f"https://api.crossref.org/works?{params}"

            data = http_get(url)
            if not data or "message" not in data:
                print(f"    No response from CrossRef for offset {offset}", flush=True)
                break

            items = data["message"].get("items", [])
            if not items:
                print(f"    No more items at offset {offset}", flush=True)
                break

            for item in items:
                doi = (item.get("DOI") or "").strip().lower()
                title_list = item.get("title", [])
                title = title_list[0].strip() if title_list else ""
                clean_title = re.sub(r'\s+', ' ', title.lower())

                # Skip if empty title or already seen
                if not title:
                    continue
                if doi and doi in seen_dois:
                    continue
                if clean_title in seen_titles:
                    continue

                if doi:
                    seen_dois.add(doi)
                if clean_title:
                    seen_titles.add(clean_title)

                item["_search_query"] = query
                all_items.append(item)
                query_added += 1

            total_results = data["message"].get("total-results", 0)
            offset += 50
            if offset >= total_results or offset >= max_per_query:
                break

            time.sleep(1.2)  # Polite delay

        print(f"    -> Added {query_added} new items (Total unique so far: {len(all_items)})", flush=True)
        time.sleep(1.0)

    # Save JSON
    json_path = os.path.join(JSON_DIR, "crossref.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Saved JSON: {json_path} ({len(all_items)} articles)", flush=True)

    # Convert to CSV
    csv_rows = []
    for i, item in enumerate(all_items, 1):
        # Authors
        authors_list = item.get("author", [])
        author_names = []
        for a in authors_list:
            if a.get("family") and a.get("given"):
                author_names.append(f"{a['family']}, {a['given']}")
            elif a.get("family"):
                author_names.append(a["family"])
            elif a.get("name"):
                author_names.append(a["name"])
        authors = "; ".join(author_names)

        # Publication Year
        pub_date = (
            item.get("published-print") or
            item.get("published-online") or
            item.get("issued") or
            item.get("created") or {}
        )
        date_parts = pub_date.get("date-parts", [[None]])[0]
        year = str(date_parts[0]) if date_parts and date_parts[0] else ""

        # Title
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""

        # Journal / Container
        container = item.get("container-title", [])
        venue = container[0] if container else ""

        # Abstract
        raw_abstract = item.get("abstract", "")
        clean_abstract = re.sub(r'<[^>]+>', '', raw_abstract).strip() if raw_abstract else ""

        doi = item.get("DOI", "")
        url = item.get("URL", f"https://doi.org/{doi}" if doi else "")

        # Duplicate key
        dup_key = make_duplicate_key(title, year)

        # Citations
        citations = item.get("is-referenced-by-count", "N/A")

        csv_rows.append({
            "Article_ID": f"CR-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "CrossRef",
            "Search_Date": SEARCH_DATE,
            "Search_Query": item.get("_search_query", "Multiple queries (Q01-Q14)"),
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": url,
            "Abstract": clean_abstract[:5000],
            "Document_Type": item.get("type", "journal-article"),
            "Language": item.get("language", "en"),
            "Duplicate_Key": dup_key,
            "Duplicate?": "",
            "Notes": f"Citations: {citations}"
        })

    csv_path = os.path.join(CSV_DIR, "crossref.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(f"[OK] Saved CSV: {csv_path} ({len(csv_rows)} rows)", flush=True)

    return len(csv_rows)

if __name__ == "__main__":
    count = search_crossref()
    print(f"\nCrossRef scraping completed: {count} unique journal articles.", flush=True)
