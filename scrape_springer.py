"""
Scraping Jurnal Akademik — Springer Nature Meta API
Menggunakan API Key resmi yang diberikan.
Hanya mengambil artikel jurnal ilmiah (contentType: Article) rentang 2018-2026.
Output: raw_json/springer.json & csv/springer.csv
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

API_KEY = "c46838bcfb518bae7d8f0b30f0cfb552"
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

def http_get_springer(query, start_record=1, page_size=20, retries=3):
    params = urllib.parse.urlencode({
        "q": query,
        "api_key": API_KEY,
        "p": page_size,
        "s": start_record
    })
    url = f"https://api.springernature.com/meta/v2/json?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "AcademicSLR/1.0"})

    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"    [HTTP {e.code}] {e.reason}", flush=True)
            if e.code == 429:
                time.sleep(5 * (attempt + 1))
            else:
                time.sleep(2)
        except Exception as e:
            print(f"    [Attempt {attempt+1} Error] {e}", flush=True)
            time.sleep(3 * (attempt + 1))
    return None

def search_springer():
    print("=" * 60, flush=True)
    print("SCRAPING SPRINGER NATURE API (API Key Aktif)", flush=True)
    print("=" * 60, flush=True)

    queries = [
        ("Q01", '"world model" video'),
        ("Q02", '"world models" video'),
        ("Q03", 'world model JEPA'),
        ("Q04", '"joint embedding predictive architecture"'),
        ("Q05", '"generative world model"'),
        ("Q06", '"diffusion world model"'),
        ("Q07", '"video world model"'),
        ("Q08", 'latent dynamics "video prediction"'),
        ("Q09", '"visual world model"'),
        ("Q10", '"action-conditioned" video world model'),
        ("Q11", 'V-JEPA video'),
        ("Q12", 'I-JEPA representation learning'),
    ]

    all_articles = []
    seen_dois = set()
    seen_titles = set()

    for qid, query in queries:
        print(f"\n[{qid}] Query: '{query}'", flush=True)
        start = 1
        query_added = 0
        max_fetch = 100  # 5 halaman @ 20 item

        while start <= max_fetch:
            data = http_get_springer(query, start_record=start, page_size=20)
            if not data or "records" not in data:
                print(f"    Tidak ada data dari Springer untuk start {start}", flush=True)
                break

            records = data.get("records", [])
            if not records:
                break

            for r in records:
                # Sesuai protokol SLR: Hanya artikel jurnal ilmiah (Article)
                content_type = r.get("contentType", "")
                if "Article" not in content_type:
                    continue

                # Filter tahun 2018 - 2026
                pub_date = r.get("publicationDate", "")
                year = pub_date[:4] if pub_date else ""
                if not (year.isdigit() and 2018 <= int(year) <= 2026):
                    continue

                doi = (r.get("doi") or "").strip().lower()
                title = clean_text(r.get("title", ""))
                clean_title_key = title.lower()

                if not title:
                    continue
                if doi and doi in seen_dois:
                    continue
                if clean_title_key in seen_titles:
                    continue

                if doi:
                    seen_dois.add(doi)
                if clean_title_key:
                    seen_titles.add(clean_title_key)

                r["_search_query"] = query
                all_articles.append(r)
                query_added += 1

            total_avail = 0
            if data.get("result") and len(data["result"]) > 0:
                total_avail = int(data["result"][0].get("total", 0))

            start += 20
            if start > total_avail or start > max_fetch:
                break

            time.sleep(1.0)

        print(f"    -> Ditambahkan {query_added} artikel jurnal unik (Total Springer: {len(all_articles)})", flush=True)
        time.sleep(1.0)

    # Simpan JSON
    json_path = os.path.join(JSON_DIR, "springer.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Simpan JSON: {json_path} ({len(all_articles)} artikel)", flush=True)

    # Simpan CSV
    csv_rows = []
    for i, r in enumerate(all_articles, 1):
        creators = r.get("creators", [])
        author_names = [clean_text(c.get("creator", "")) for c in creators if c.get("creator")]
        authors = "; ".join(author_names)

        pub_date = r.get("publicationDate", "")
        year = pub_date[:4] if pub_date else ""

        title = clean_text(r.get("title", ""))
        venue = clean_text(r.get("publicationName", ""))
        abstract = clean_text(r.get("abstract", ""))
        doi = r.get("doi", "")
        url = f"https://doi.org/{doi}" if doi else ""

        csv_rows.append({
            "Article_ID": f"SN-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "Springer Nature",
            "Search_Date": SEARCH_DATE,
            "Search_Query": r.get("_search_query", "Multiple queries"),
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
            "Notes": f"Publisher: Springer Nature | Type: {r.get('contentType', 'Article')}"
        })

    csv_path = os.path.join(CSV_DIR, "springer.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(f"[OK] Simpan CSV: {csv_path} ({len(csv_rows)} baris)", flush=True)

    return len(csv_rows)

if __name__ == "__main__":
    count = search_springer()
    print(f"\nSelesai! Berhasil mengumpulkan {count} artikel jurnal unik dari Springer Nature.", flush=True)
