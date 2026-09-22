"""
Scraping Jurnal Akademik — Elsevier Scopus & ScienceDirect API
Menggunakan API Key resmi: 51938f21ad09aae4bb772cf7b69a140a
Output:
  - raw_json/scopus.json & csv/scopus.csv
  - raw_json/sciencedirect.json & csv/sciencedirect.csv
"""

import json
import csv
import os
import time
import re
import html
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "raw_json")
CSV_DIR = os.path.join(BASE_DIR, "csv")
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

API_KEY = "51938f21ad09aae4bb772cf7b69a140a"
SEARCH_DATE = datetime.now().strftime("%Y-%m-%d")

CSV_HEADERS = [
    "Article_ID", "Source_Type", "Database/Source", "Search_Date",
    "Search_Query", "Title", "Authors", "Year", "Journal/Conference",
    "DOI", "URL", "Abstract", "Document_Type", "Language",
    "Duplicate_Key", "Duplicate?", "Notes"
]

def clean_text(text):
    if not text:
        return ""
    t = html.unescape(str(text))
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'(\b[a-zA-Z]+)-\s+([a-zA-Z]+\b)', r'\1\2', t)
    t = re.sub(r'[\r\n\t]+', ' ', t)
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()

def make_duplicate_key(title, year):
    if not title:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    words = clean.split()[:7]
    base = "_".join(words)
    return f"{base}_{year}" if year else base

# ============================================================
# 1. SCOPUS
# ============================================================
def scrape_scopus():
    print("=" * 60, flush=True)
    print("SCRAPING ELSEVIER SCOPUS API", flush=True)
    print("=" * 60, flush=True)

    scopus_queries = [
        ("Q01_exact", 'TITLE-ABS-KEY(("world model" OR "world models" OR "learned dynamics model") AND ("JEPA" OR "joint embedding predictive architecture" OR "generative world model" OR "diffusion world model") AND ("video prediction" OR "planning" OR "model-based RL")) AND PUBYEAR > 2017 AND PUBYEAR < 2027 AND DOCTYPE(ar)'),
        ("Q02_video_gen_jepa", 'TITLE-ABS-KEY(("world model" OR "world models") AND ("video" OR "visual") AND ("JEPA" OR "generative" OR "diffusion" OR "autoregressive")) AND PUBYEAR > 2017 AND DOCTYPE(ar)'),
        ("Q03_jepa_vision", 'TITLE-ABS-KEY(("JEPA" OR "joint embedding predictive architecture" OR "V-JEPA" OR "I-JEPA") AND ("video" OR "visual" OR "image" OR "representation")) AND PUBYEAR > 2017 AND DOCTYPE(ar)'),
        ("Q04_gen_wm", 'TITLE-ABS-KEY(("generative world model" OR "diffusion world model" OR "video world model")) AND PUBYEAR > 2017 AND DOCTYPE(ar)'),
        ("Q05_wm_video_pred", 'TITLE-ABS-KEY(("world model" OR "world models") AND ("video prediction" OR "frame prediction" OR "visual planning")) AND PUBYEAR > 2017 AND DOCTYPE(ar)'),
        ("Q06_action_wm", 'TITLE-ABS-KEY(("action-conditioned" AND "world model" AND video)) AND PUBYEAR > 2017 AND DOCTYPE(ar)'),
    ]

    all_items = []
    seen_dois = set()
    seen_titles = set()

    for qid, query in scopus_queries:
        print(f"\n[{qid}] Query: {query[:75]}...", flush=True)
        start = 0
        query_added = 0
        max_fetch = 100

        while start < max_fetch:
            params = urllib.parse.urlencode({
                "query": query,
                "count": 25,
                "start": start,
                "view": "STANDARD"
            })
            url = f"https://api.elsevier.com/content/search/scopus?{params}"
            req = urllib.request.Request(url, headers={
                "X-ELS-APIKey": API_KEY,
                "Accept": "application/json",
                "User-Agent": "AcademicSLR/1.0"
            })

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"    Gagal pada start {start}: {e}", flush=True)
                break

            results = data.get("search-results", {})
            entries = results.get("entry", [])
            if not entries or (len(entries) == 1 and "error" in entries[0]):
                break

            for it in entries:
                doi = (it.get("prism:doi") or "").strip().lower()
                title = clean_text(it.get("dc:title", ""))
                clean_t = title.lower()

                if not title:
                    continue
                if doi and doi in seen_dois:
                    continue
                if clean_t in seen_titles:
                    continue

                if doi:
                    seen_dois.add(doi)
                if clean_t:
                    seen_titles.add(clean_t)

                it["_search_query"] = query
                all_items.append(it)
                query_added += 1

            total_records = int(results.get("opensearch:totalResults", 0))
            start += 25
            if start >= total_records or start >= max_fetch:
                break

            time.sleep(1.0)

        print(f"    -> Ditambahkan {query_added} artikel unik (Total Scopus: {len(all_items)})", flush=True)
        time.sleep(0.5)

    # Simpan JSON
    json_path = os.path.join(JSON_DIR, "scopus.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Simpan JSON Scopus: {json_path} ({len(all_items)} artikel)", flush=True)

    # Simpan CSV
    csv_rows = []
    for i, it in enumerate(all_items, 1):
        creator = clean_text(it.get("dc:creator", ""))
        title = clean_text(it.get("dc:title", ""))
        venue = clean_text(it.get("prism:publicationName", ""))
        doi = it.get("prism:doi", "")
        cover_date = it.get("prism:coverDate", "")
        year = cover_date[:4] if cover_date else ""
        url = f"https://doi.org/{doi}" if doi else ""
        abstract = clean_text(it.get("dc:description", ""))

        csv_rows.append({
            "Article_ID": f"SCOPUS-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "Scopus",
            "Search_Date": SEARCH_DATE,
            "Search_Query": it.get("_search_query", "Multiple queries"),
            "Title": title,
            "Authors": creator,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": url,
            "Abstract": abstract[:5000],
            "Document_Type": "journal-article",
            "Language": "en",
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Cited by: {it.get('citedby-count', 'N/A')}"
        })

    csv_path = os.path.join(CSV_DIR, "scopus.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in csv_rows:
            writer.writerow(r)

    print(f"[OK] Simpan CSV Scopus: {csv_path} ({len(csv_rows)} baris)", flush=True)
    return len(csv_rows)


# ============================================================
# 2. SCIENCEDIRECT
# ============================================================
def scrape_sciencedirect():
    print("\n" + "=" * 60, flush=True)
    print("SCRAPING ELSEVIER SCIENCEDIRECT API", flush=True)
    print("=" * 60, flush=True)

    sd_queries = [
        ("Q01_protocol", '("world model" OR "world models") AND ("JEPA" OR "generative" OR "diffusion") AND ("video prediction" OR "planning" OR "probing")'),
        ("Q02_video_wm", '("world model" OR "world models") AND ("video prediction" OR "video generation" OR "visual planning")'),
        ("Q03_jepa", '("joint embedding predictive architecture" OR "JEPA" OR "V-JEPA") AND (video OR visual)'),
        ("Q04_gen_wm", '("generative world model" OR "diffusion world model" OR "video world model")'),
    ]

    all_items = []
    seen_dois = set()
    seen_titles = set()

    for qid, query in sd_queries:
        print(f"\n[{qid}] Query: {query[:75]}...", flush=True)
        start = 0
        query_added = 0
        max_fetch = 100

        while start < max_fetch:
            params = urllib.parse.urlencode({
                "query": query,
                "count": 25,
                "start": start,
                "date": "2018-2026"
            })
            url = f"https://api.elsevier.com/content/search/sciencedirect?{params}"
            req = urllib.request.Request(url, headers={
                "X-ELS-APIKey": API_KEY,
                "Accept": "application/json",
                "User-Agent": "AcademicSLR/1.0"
            })

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"    Gagal pada start {start}: {e}", flush=True)
                break

            results = data.get("search-results", {})
            entries = results.get("entry", [])
            if not entries or (len(entries) == 1 and "error" in entries[0]):
                break

            for it in entries:
                doi = (it.get("prism:doi") or "").strip().lower()
                title = clean_text(it.get("dc:title", ""))
                clean_t = title.lower()

                if not title:
                    continue
                if doi and doi in seen_dois:
                    continue
                if clean_t in seen_titles:
                    continue

                if doi:
                    seen_dois.add(doi)
                if clean_t:
                    seen_titles.add(clean_t)

                it["_search_query"] = query
                all_items.append(it)
                query_added += 1

            total_records = int(results.get("opensearch:totalResults", 0))
            start += 25
            if start >= total_records or start >= max_fetch:
                break

            time.sleep(1.0)

        print(f"    -> Ditambahkan {query_added} artikel unik (Total ScienceDirect: {len(all_items)})", flush=True)
        time.sleep(0.5)

    # Simpan JSON
    json_path = os.path.join(JSON_DIR, "sciencedirect.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Simpan JSON ScienceDirect: {json_path} ({len(all_items)} artikel)", flush=True)

    # Simpan CSV
    csv_rows = []
    for i, it in enumerate(all_items, 1):
        # Authors
        authors = clean_text(it.get("dc:creator", "") or it.get("authors", ""))
        title = clean_text(it.get("dc:title", ""))
        venue = clean_text(it.get("prism:publicationName", ""))
        doi = it.get("prism:doi", "")
        cover_date = it.get("prism:coverDate", "")
        year = cover_date[:4] if cover_date else ""
        url = f"https://doi.org/{doi}" if doi else ""
        abstract = clean_text(it.get("dc:description", ""))

        csv_rows.append({
            "Article_ID": f"SD-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "ScienceDirect",
            "Search_Date": SEARCH_DATE,
            "Search_Query": it.get("_search_query", "Multiple queries"),
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": url,
            "Abstract": abstract[:5000],
            "Document_Type": "journal-article",
            "Language": "en",
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Publisher: Elsevier ScienceDirect"
        })

    csv_path = os.path.join(CSV_DIR, "sciencedirect.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in csv_rows:
            writer.writerow(r)

    print(f"[OK] Simpan CSV ScienceDirect: {csv_path} ({len(csv_rows)} baris)", flush=True)
    return len(csv_rows)

if __name__ == "__main__":
    scopus_count = scrape_scopus()
    sd_count = scrape_sciencedirect()
    print("\n" + "=" * 60, flush=True)
    print(f"SELESAI ELSEVIER API!", flush=True)
    print(f"  - Scopus        : {scopus_count} artikel", flush=True)
    print(f"  - ScienceDirect : {sd_count} artikel", flush=True)
    print("=" * 60, flush=True)
