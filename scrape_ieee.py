"""
Scraping Jurnal Akademik — IEEE Xplore API
Menggunakan API Key resmi yang diberikan: ynsq4u783dx2wpb8xe3sk49t
Menargetkan jurnal IEEE (content_type: Journals) tahun 2018-2026 sesuai protokol SLR.
Output: raw_json/ieee.json & csv/ieee.csv
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

# Baca API Key dari .env atau default
API_KEY = "ynsq4u783dx2wpb8xe3sk49t"
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

def test_ieee_key():
    test_url = f"https://ieeexploreapi.ieee.org/api/v1/search/articles?apikey={API_KEY}&format=json&max_records=1&querytext=robot"
    req = urllib.request.Request(test_url, headers={"User-Agent": "AcademicSLR/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return True, "Active"
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, "Menunggu Aktivasi Admin IEEE (Awaiting IEEE activation - Status 403)"
        return False, f"HTTP Error {e.code}: {e.reason}"
    except Exception as e:
        return False, f"Error: {e}"

def search_ieee():
    print("=" * 60)
    print("SCRAPING IEEE XPLORE REST API")
    print(f"API Key: {API_KEY}")
    print("=" * 60)

    # 1. Cek status aktivasi key
    active, msg = test_ieee_key()
    if not active:
        print(f"\n[PERHATIAN] API Key IEEE belum aktif: {msg}")
        print("Sesuai email dari IEEE Xplore, permohonan sedang menunggu persetujuan.")
        print("Aktivasi dilakukan pada jam kerja US Eastern (08:00 - 17:00 ET).")
        print("Begitu menerima email persetujuan, jalankan script ini kembali: python scrape_ieee.py")
        return 0

    print("\n[OK] API Key IEEE sudah aktif! Memulai penarikan artikel...")

    # Query spesifik sesuai Search_Strategy di Excel
    ieee_queries = [
        ("Q01", '("world model" OR "world models") AND ("video" OR "video prediction")'),
        ("Q02", '("joint embedding predictive architecture" OR "JEPA") AND video'),
        ("Q03", '("generative world model" OR "diffusion world model")'),
        ("Q04", '("latent dynamics" OR "learned dynamics") AND video'),
        ("Q05", '("V-JEPA" OR "I-JEPA")'),
        ("Q06", '"world model" AND ("planning" OR "reinforcement learning") AND visual'),
    ]

    all_articles = []
    seen_dois = set()
    seen_titles = set()

    for qid, query in ieee_queries:
        print(f"\n[{qid}] Query: '{query}'")
        start = 1
        query_added = 0
        max_fetch = 100  # IEEE gratis batasan 200 calls/day, p=25 per call

        while start <= max_fetch:
            params = urllib.parse.urlencode({
                "apikey": API_KEY,
                "format": "json",
                "querytext": query,
                "content_type": "Journals",
                "start_year": "2018",
                "end_year": "2026",
                "max_records": 25,
                "start_record": start
            })
            url = f"https://ieeexploreapi.ieee.org/api/v1/search/articles?{params}"
            req = urllib.request.Request(url, headers={"User-Agent": "AcademicSLR/1.0"})

            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except Exception as e:
                print(f"    Gagal mengambil start {start}: {e}")
                break

            articles = data.get("articles", [])
            if not articles:
                break

            for art in articles:
                doi = (art.get("doi") or "").strip().lower()
                title = clean_text(art.get("title", ""))
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

                art["_search_query"] = query
                all_articles.append(art)
                query_added += 1

            total_records = int(data.get("total_records", 0))
            start += 25
            if start > total_records or start > max_fetch:
                break

            time.sleep(1.0)

        print(f"    -> Ditambahkan {query_added} artikel jurnal unik (Total IEEE: {len(all_articles)})")
        time.sleep(1.0)

    # Simpan JSON
    json_path = os.path.join(JSON_DIR, "ieee.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)
    print(f"\n[OK] Simpan JSON: {json_path} ({len(all_articles)} artikel)")

    # Simpan CSV
    csv_rows = []
    for i, art in enumerate(all_articles, 1):
        authors_obj = art.get("authors", {}).get("authors", [])
        author_names = [clean_text(a.get("full_name", "")) for a in authors_obj if a.get("full_name")]
        authors = "; ".join(author_names)

        year = str(art.get("publication_year", ""))
        title = clean_text(art.get("title", ""))
        venue = clean_text(art.get("publication_title", ""))
        abstract = clean_text(art.get("abstract", ""))
        doi = art.get("doi", "")
        url = art.get("html_url", f"https://doi.org/{doi}" if doi else "")

        csv_rows.append({
            "Article_ID": f"IEEE-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "IEEE Xplore",
            "Search_Date": SEARCH_DATE,
            "Search_Query": art.get("_search_query", "Multiple queries"),
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
            "Notes": f"Citations: {art.get('citing_paper_count', 'N/A')} | Content: {art.get('content_type', 'Journals')}"
        })

    csv_path = os.path.join(CSV_DIR, "ieee.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in csv_rows:
            writer.writerow(row)
    print(f"[OK] Simpan CSV: {csv_path} ({len(csv_rows)} baris)")

    return len(csv_rows)

if __name__ == "__main__":
    count = search_ieee()
