"""
Konsolidasi & Deduplikasi Hasil Scraping
Menggabungkan data dari Semantic Scholar, OpenAlex, CrossRef, dan PubMed.
Menghasilkan:
1. csv/all_combined.csv (semua artikel dengan penanda duplikat)
2. csv/all_unique.csv (hanya artikel unik)
3. summary_report.md (statistik lengkap per database, overlap, tahun)
"""

import csv
import os
import re
from collections import defaultdict, Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "csv")

DATABASES = ["openalex", "crossref", "semantic_scholar", "springer", "scopus", "sciencedirect", "ieee", "pubmed"]

CSV_HEADERS = [
    "Article_ID", "Source_Type", "Database/Source", "Search_Date",
    "Search_Query", "Title", "Authors", "Year", "Journal/Conference",
    "DOI", "URL", "Abstract", "Document_Type", "Language",
    "Duplicate_Key", "Duplicate?", "Notes"
]

def clean_title(title):
    if not title:
        return ""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    return " ".join(clean.split())

def make_norm_key(title, year):
    ct = clean_title(title)
    words = ct.split()[:7]
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

def run_consolidation():
    all_records = []
    stats_per_db = {}
    
    for db in DATABASES:
        path = os.path.join(CSV_DIR, f"{db}.csv")
        if not os.path.exists(path):
            print(f"File {path} belum ada, lewati...")
            continue
        
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            stats_per_db[db] = len(rows)
            all_records.extend(rows)

    print("=" * 60)
    print("STATISTIK SEBELUM DEDUPLIKASI:")
    for db, count in stats_per_db.items():
        print(f"  - {db.replace('_', ' ').title():<20}: {count} artikel")
    print(f"  TOTAL KESELURUHAN: {len(all_records)} entri")
    print("=" * 60)

    # Cross-source Deduplication
    seen_dois = {}       # doi -> first Article_ID
    seen_titles = {}     # norm_key -> first Article_ID
    
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
        key = make_norm_key(title, year)
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

    # Save combined
    combined_path = os.path.join(CSV_DIR, "all_combined.csv")
    with open(combined_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in combined_records:
            writer.writerow(r)

    # Save unique only
    unique_path = os.path.join(CSV_DIR, "all_unique.csv")
    with open(unique_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for r in unique_records:
            writer.writerow(r)

    # Statistics & Breakdown
    year_dist = Counter([r.get("Year", "Unknown") for r in unique_records])
    db_unique_dist = Counter([r.get("Database/Source", "Unknown") for r in unique_records])

    summary_text = f"""# Ringkasan Hasil Scraping & Deduplikasi Jurnal Akademik
**Topik Penelitian**: Arsitektur World Model pada Domain Video: Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif  
**Rentang Pencarian**: 2018 – 2026  
**Format Sesuai**: Sheet `Raw_Articles` pada Excel Protokol SLR  

---

## 1. Statistik Hasil per Basis Data

| No | Basis Data / Sumber | Format / API | Jumlah Mentah | Jumlah Unik Primer |
|---|---|---|---|---|
"""
    db_order = [
        ("crossref", "CrossRef", "api.crossref.org (Polite Pool)"),
        ("openalex", "OpenAlex", "api.openalex.org"),
        ("scopus", "Scopus", "api.elsevier.com (API Key)"),
        ("sciencedirect", "ScienceDirect", "api.elsevier.com (API Key)"),
        ("springer", "Springer Nature", "api.springernature.com (API Key)"),
        ("semantic_scholar", "Semantic Scholar", "api.semanticscholar.org"),
        ("pubmed", "PubMed", "eutils.ncbi.nlm.nih.gov"),
    ]
    
    no = 1
    for db_key, db_title, api_desc in db_order:
        if db_key in stats_per_db:
            summary_text += f"| {no} | **{db_title}** | `{api_desc}` | {stats_per_db[db_key]} | {db_unique_dist.get(db_title, 0)} |\n"
            no += 1

    summary_text += f"""| | **TOTAL KESELURUHAN** | | **{len(all_records)}** | **{len(unique_records)}** |

- **Total Entri Mentah Terkumpul**: {len(all_records)} artikel
- **Total Duplikat Lintas Basis Data**: {len(all_records) - len(unique_records)} artikel
- **Total Artikel Unik (Siap Screening)**: **{len(unique_records)} artikel**

---

## 2. Distribusi Tahun Terbit (Artikel Unik)

| Tahun | Jumlah Artikel | Persentase |
|---|---|---|
"""
    sorted_years = sorted([y for y in year_dist.keys() if y.isdigit()], reverse=True)
    for y in sorted_years:
        cnt = year_dist[y]
        pct = (cnt / len(unique_records)) * 100 if unique_records else 0
        summary_text += f"| {y} | {cnt} | {pct:.1f}% |\n"
    
    other_cnt = sum(year_dist[y] for y in year_dist if not y.isdigit())
    if other_cnt > 0:
        pct = (other_cnt / len(unique_records)) * 100 if unique_records else 0
        summary_text += f"| N/A / Lainnya | {other_cnt} | {pct:.1f}% |\n"

    summary_text += f"""
---

## 3. Tumpang-Tindih Antar Basis Data (Overlap Matrix)

| Pasangan Basis Data | Jumlah Artikel Duplikat yang Ditemukan Bersama |
|---|---|
"""
    for pair, count in sorted(overlap_pairs.items(), key=lambda x: x[1], reverse=True):
        summary_text += f"| {' & '.join(pair)} | {count} artikel |\n"

    summary_text += f"""
---

## 4. Lokasi File Output

1. **JSON per Basis Data** (Folder `raw_json/`):
   - `raw_json/crossref.json`
   - `raw_json/openalex.json`
   - `raw_json/scopus.json`
   - `raw_json/sciencedirect.json`
   - `raw_json/springer.json`
   - `raw_json/semantic_scholar.json`
   - `raw_json/pubmed.json`

2. **CSV per Basis Data** (Folder `csv/`):
   - `csv/crossref.csv`
   - `csv/openalex.csv`
   - `csv/scopus.csv`
   - `csv/sciencedirect.csv`
   - `csv/springer.csv`
   - `csv/semantic_scholar.csv`
   - `csv/pubmed.csv`

3. **CSV Konsolidasi**:
   - `csv/all_combined.csv` ({len(all_records)} baris, mencakup seluruh entri dengan penanda duplikat)
   - `csv/all_unique.csv` ({len(unique_records)} baris, hanya artikel unik untuk tahap screening berikutnya)

Semua kolom CSV sudah 100% presisi mengikuti struktur header pada sheet **Raw_Articles**:
`Article_ID`, `Source_Type`, `Database/Source`, `Search_Date`, `Search_Query`, `Title`, `Authors`, `Year`, `Journal/Conference`, `DOI`, `URL`, `Abstract`, `Document_Type`, `Language`, `Duplicate_Key`, `Duplicate?`, `Notes`.
"""

    summary_path = os.path.join(BASE_DIR, "scraping_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    print("\n" + "=" * 60)
    print(f"KONSOLIDASI SELESAI!")
    print(f"  - Total Mentah   : {len(all_records)}")
    print(f"  - Duplikat       : {len(all_records) - len(unique_records)}")
    print(f"  - Total Unik     : {len(unique_records)}")
    print(f"  - File Gabungan  : {combined_path}")
    print(f"  - File Unik      : {unique_path}")
    print(f"  - Ringkasan      : {summary_path}")
    print("=" * 60)

if __name__ == "__main__":
    run_consolidation()
