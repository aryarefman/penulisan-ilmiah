"""
Pembersihan dan Perbaikan Total Dataset Scraping (JSON & CSV)
Masalah yang diperbaiki:
1. Newlines (\r, \n, \t) di dalam Abstract/Title yang membuat baris CSV terpotong-potong di VS Code / Excel.
2. Sisa tag HTML/XML (<jats:p>, <sup>, <b>, &amp;, dll) di Title dan Abstract.
3. Artikel tidak relevan akibat singkatan jurnal "JEPA" (Jurnal Ekonomi Pertanian dan Agribisnis, Journal of Economic, Public, and Accounting, dsb) atau "World" (World Neurosurgery).
4. Penambahan field "abstract" yang dapat dibaca manusia pada openalex.json (sebelumnya hanya inverted index).
5. Memastikan 100% konsistensi: 1 baris CSV = 1 baris fisik di file (tidak ada split line).
"""

import json
import csv
import os
import re
import html
from collections import Counter, defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "raw_json")
CSV_DIR = os.path.join(BASE_DIR, "csv")

CSV_HEADERS = [
    "Article_ID", "Source_Type", "Database/Source", "Search_Date",
    "Search_Query", "Title", "Authors", "Year", "Journal/Conference",
    "DOI", "URL", "Abstract", "Document_Type", "Language",
    "Duplicate_Key", "Duplicate?", "Notes"
]

NON_CS_VENUE_KEYWORDS = [
    'economic', 'pertanian', 'agribisnis', 'accounting', 'keuangan',
    'educational psychology', 'neurosurgery', 'dentistry', 'nursing',
    'veterinary', 'dermatology', 'urology', 'cardiology', 'orthopedic',
    'gastroenterology', 'ophthalmology', 'oncology nursing', 'obstetrics',
    'gynecology', 'clinical pediatrics', 'anesthesiology'
]

def clean_text(text):
    if not text:
        return ""
    # 1. Unescape HTML entities (&amp;, &lt;, &gt;, &quot;, &#39;, dll)
    t = html.unescape(str(text))
    # 2. Remove XML / HTML / JATS tags
    t = re.sub(r'<[^>]+>', ' ', t)
    # 3. Fix hyphenated line breaks from OCR/PDF (e.g. "Architec- ture" -> "Architecture")
    t = re.sub(r'(\b[a-zA-Z]+)-\s+([a-zA-Z]+\b)', r'\1\2', t)
    # 4. Replace newlines, carriage returns, tabs with a single space
    t = re.sub(r'[\r\n\t]+', ' ', t)
    # 5. Collapse multiple whitespace
    t = re.sub(r'\s{2,}', ' ', t)
    return t.strip()

def make_duplicate_key(title, year):
    if not title:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    words = clean.split()[:7]
    base = "_".join(words)
    return f"{base}_{year}" if year else base

def normalize_doi(doi):
    if not doi:
        return ""
    doi = doi.strip().lower()
    for prefix in ["https://doi.org/", "http://doi.org/", "doi:"]:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.strip()

def reconstruct_openalex_abstract(inverted_index):
    if not inverted_index:
        return ""
    pos_word = []
    for word, positions in inverted_index.items():
        for pos in positions:
            pos_word.append((pos, word))
    pos_word.sort(key=lambda x: x[0])
    return " ".join(w for _, w in pos_word)

def repair_crossref():
    print("\n[1/4] Memperbaiki CrossRef (JSON & CSV)...")
    json_path = os.path.join(JSON_DIR, "crossref.json")
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    cleaned_items = []
    dropped_count = 0

    for it in items:
        venues = [v.lower() for v in it.get("container-title", [])]
        venue_str = " ".join(venues)
        
        # Filter false-positive non-CS journals
        if any(kw in venue_str for kw in NON_CS_VENUE_KEYWORDS):
            dropped_count += 1
            continue

        # Clean fields in JSON item
        title_list = it.get("title", [])
        if title_list:
            it["title"] = [clean_text(title_list[0])]
        
        if it.get("abstract"):
            it["abstract"] = clean_text(it["abstract"])

        container = it.get("container-title", [])
        if container:
            it["container-title"] = [clean_text(container[0])]

        cleaned_items.append(it)

    print(f"  - Total awal       : {len(items)}")
    print(f"  - Dibuang (non-CS) : {dropped_count} artikel jurnal non-CS (akronim JEPA/World)")
    print(f"  - Tersisa valid    : {len(cleaned_items)}")

    # Simpan kembali JSON bersih
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_items, f, ensure_ascii=False, indent=2)

    # Buat CSV CrossRef baru yang 100% bebas newline dalam sel
    csv_rows = []
    for i, it in enumerate(cleaned_items, 1):
        authors_list = it.get("author", [])
        author_names = []
        for a in authors_list:
            if a.get("family") and a.get("given"):
                author_names.append(f"{a['family']}, {a['given']}")
            elif a.get("family"):
                author_names.append(a["family"])
            elif a.get("name"):
                author_names.append(a["name"])
        authors = clean_text("; ".join(author_names))

        pub_date = it.get("published-print") or it.get("published-online") or it.get("issued") or it.get("created") or {}
        date_parts = pub_date.get("date-parts", [[None]])[0]
        year = str(date_parts[0]) if date_parts and date_parts[0] else ""

        title = it.get("title", [""])[0] if it.get("title") else ""
        venue = it.get("container-title", [""])[0] if it.get("container-title") else ""
        abstract = it.get("abstract", "")
        doi = it.get("DOI", "")
        url = it.get("URL", f"https://doi.org/{doi}" if doi else "")

        csv_rows.append({
            "Article_ID": f"CR-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "CrossRef",
            "Search_Date": "2026-09-22",
            "Search_Query": it.get("_search_query", "Multiple queries (Q01-Q14)"),
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": url,
            "Abstract": abstract[:5000],
            "Document_Type": clean_text(it.get("type", "journal-article")),
            "Language": clean_text(it.get("language", "en")),
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Citations: {it.get('is-referenced-by-count', 'N/A')}"
        })

    csv_path = os.path.join(CSV_DIR, "crossref.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in csv_rows:
            writer.writerow(r)

    print(f"  - CSV diperbaiki   : {csv_path} ({len(csv_rows)} baris)")
    return len(csv_rows)

def repair_openalex():
    print("\n[2/4] Memperbaiki OpenAlex (JSON & CSV)...")
    json_path = os.path.join(JSON_DIR, "openalex.json")
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Tambahkan field 'abstract' yang langsung bisa dibaca manusia di JSON
    for it in items:
        if not it.get("abstract") and it.get("abstract_inverted_index"):
            it["abstract"] = clean_text(reconstruct_openalex_abstract(it["abstract_inverted_index"]))
        elif it.get("abstract"):
            it["abstract"] = clean_text(it["abstract"])
        it["title"] = clean_text(it.get("title", ""))

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    # Bersihkan CSV OpenAlex
    csv_path = os.path.join(CSV_DIR, "openalex.csv")
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        for k in CSV_HEADERS:
            r[k] = clean_text(r.get(k, ""))
        r["Duplicate_Key"] = make_duplicate_key(r["Title"], r["Year"])

    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"  - JSON & CSV diperbaiki : {len(rows)} baris")
    return len(rows)

def repair_semantic_scholar():
    print("\n[3/4] Memperbaiki Semantic Scholar (JSON & CSV)...")
    json_path = os.path.join(JSON_DIR, "semantic_scholar.json")
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    for it in items:
        it["title"] = clean_text(it.get("title", ""))
        if it.get("abstract"):
            it["abstract"] = clean_text(it["abstract"])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(CSV_DIR, "semantic_scholar.csv")
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        for k in CSV_HEADERS:
            r[k] = clean_text(r.get(k, ""))
        r["Duplicate_Key"] = make_duplicate_key(r["Title"], r["Year"])

    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"  - JSON & CSV diperbaiki : {len(rows)} baris")
    return len(rows)

def repair_pubmed():
    print("\n[4/4] Memperbaiki PubMed (JSON & CSV)...")
    json_path = os.path.join(JSON_DIR, "pubmed.json")
    with open(json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    for it in items:
        it["title"] = clean_text(it.get("title", ""))
        if it.get("abstract"):
            it["abstract"] = clean_text(it["abstract"])

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    csv_path = os.path.join(CSV_DIR, "pubmed.csv")
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        for k in CSV_HEADERS:
            r[k] = clean_text(r.get(k, ""))
        r["Duplicate_Key"] = make_duplicate_key(r["Title"], r["Year"])

    with open(csv_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"  - JSON & CSV diperbaiki : {len(rows)} baris")
    return len(rows)

def re_consolidate():
    print("\n" + "=" * 60)
    print("RE-KONSOLIDASI & DEDUPLIKASI LINTAS SUMBER...")
    print("=" * 60)
    
    all_records = []
    stats_per_db = {}
    
    for db in ["openalex", "crossref", "semantic_scholar", "pubmed"]:
        path = os.path.join(CSV_DIR, f"{db}.csv")
        with open(path, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            stats_per_db[db] = len(rows)
            all_records.extend(rows)

    seen_dois = {}
    seen_titles = {}
    unique_records = []
    combined_records = []
    overlap_pairs = defaultdict(int)
    db_by_id = {}

    for row in all_records:
        aid = row["Article_ID"]
        db = row["Database/Source"]
        db_by_id[aid] = db
        
        doi = normalize_doi(row.get("DOI", ""))
        title = row.get("Title", "")
        year = row.get("Year", "")
        key = make_duplicate_key(title, year)
        row["Duplicate_Key"] = key

        is_dup = False
        duplicate_of = None

        if doi and doi in seen_dois:
            is_dup = True
            duplicate_of = seen_dois[doi]
        elif key and key in seen_titles:
            is_dup = True
            duplicate_of = seen_titles[key]

        if is_dup:
            row["Duplicate?"] = "Yes"
            orig_db = db_by_id.get(duplicate_of, "Unknown")
            row["Notes"] = (row.get("Notes", "") + f" | Duplicate of {duplicate_of} ({orig_db})").strip(" |")
            pair = tuple(sorted([orig_db, db]))
            overlap_pairs[pair] += 1
        else:
            row["Duplicate?"] = "No"
            if doi:
                seen_dois[doi] = aid
            if key:
                seen_titles[key] = aid
            unique_records.append(row)

        combined_records.append(row)

    # Simpan combined
    combined_path = os.path.join(CSV_DIR, "all_combined.csv")
    with open(combined_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in combined_records:
            writer.writerow(r)

    # Simpan unique
    unique_path = os.path.join(CSV_DIR, "all_unique.csv")
    with open(unique_path, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in unique_records:
            writer.writerow(r)

    # Validasi fisik baris
    print("\n--- VALIDASI AKHIR FILE CSV (1 ROW = 1 LINE) ---")
    for fn in ["openalex", "crossref", "semantic_scholar", "pubmed", "all_combined", "all_unique"]:
        cp = os.path.join(CSV_DIR, f"{fn}.csv")
        with open(cp, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        with open(cp, "r", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
        
        status = "PASSED (100% RAPI)" if len(lines) == len(rows) else "FAILED MISMATCH"
        print(f"  {fn:<20}.csv: {len(lines)} baris teks == {len(rows)} baris CSV -> {status}")

    print("\n" + "=" * 60)
    print(f"SELESAI DIPERBAIKI!")
    print(f"  - Total Mentah Bersih : {len(all_records)}")
    print(f"  - Duplikat Lintas DB  : {len(all_records) - len(unique_records)}")
    print(f"  - Total Unik Siap SLR : {len(unique_records)}")
    print("=" * 60)

if __name__ == "__main__":
    repair_crossref()
    repair_openalex()
    repair_semantic_scholar()
    repair_pubmed()
    re_consolidate()
