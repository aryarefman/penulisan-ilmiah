#!/usr/bin/env python3
"""
Generate a compact markdown summary table — one line per article, no abstracts.
Formal academic format without emojis.
"""

import csv
import re
import sys
from collections import defaultdict
from datetime import datetime

CSV_FILE = r"csv/all_unique.csv"
OUTPUT_MD = r"literature_summary.md"

def clean(text):
    if not text: return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def shorten(text, n):
    if not text: return "—"
    text = clean(text)
    return text[:n] + "…" if len(text) > n else text

def main():
    articles = []
    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            articles.append(row)

    by_db = defaultdict(list)
    for a in articles:
        by_db[a.get("Database/Source","Unknown").strip()].append(a)

    for db in by_db:
        by_db[db].sort(key=lambda a: (-int(float(a.get("Year","0") or "0")), a.get("Title","").lower()))

    db_order = ["CrossRef","OpenAlex","Springer Nature","ScienceDirect",
                "Semantic Scholar","Scopus","PubMed","IEEE Xplore"]
    for db in sorted(by_db.keys()):
        if db not in db_order: db_order.append(db)

    # Year distribution
    year_dist = defaultdict(int)
    for a in articles:
        try: year_dist[int(float(a.get("Year","0") or "0"))] += 1
        except: pass

    lines = []
    lines.append("# Ringkasan Literatur — Systematic Literature Review")
    lines.append("")
    lines.append("**Topik:** Arsitektur World Model pada Domain Video: Perbandingan JEPA dan Generatif  ")
    lines.append(f"**Tanggal Pembuatan:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"**Total Artikel Unik:** {len(articles):,}  ")
    lines.append(f"**Rentang Tahun:** 2018 – 2026")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Stats
    lines.append("## 1. Ikhtisar Distribusi Basis Data")
    lines.append("")
    lines.append("| No | Basis Data | Jumlah Artikel | Persentase |")
    lines.append("|:---:|:---|:---:|:---:|")
    for idx, db in enumerate(db_order, 1):
        if db in by_db:
            n = len(by_db[db])
            lines.append(f"| {idx} | {db} | {n:,} | {n/len(articles)*100:.1f}% |")
    lines.append(f"| | **Total** | **{len(articles):,}** | **100.0%** |")
    lines.append("")

    lines.append("## 2. Distribusi Tahun Publikasi")
    lines.append("")
    lines.append("| Tahun | " + " | ".join(str(y) for y in sorted(year_dist.keys())) + " |")
    lines.append("|:---|" + "|".join(":---:" for _ in year_dist) + "|")
    lines.append("| Jumlah | " + " | ".join(str(year_dist[y]) for y in sorted(year_dist.keys())) + " |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Per-database tables
    lines.append("## 3. Katalog Artikel per Basis Data")
    lines.append("")

    for db in db_order:
        if db not in db_order or db not in by_db:
            continue
        arts = by_db[db]

        lines.append(f"### Basis Data: {db} ({len(arts):,} artikel)")
        lines.append("")
        lines.append("| No | Tahun | Judul Artikel | Penulis | Jurnal / Konferensi | DOI |")
        lines.append("|:---:|:---:|:---|:---|:---|:---:|")

        for i, a in enumerate(arts, 1):
            year = a.get("Year","")
            try: year = str(int(float(year)))
            except: pass

            title = shorten(a.get("Title",""), 80)
            
            raw_authors = clean(a.get("Authors",""))
            if raw_authors:
                auth_list = [x.strip() for x in raw_authors.split(";") if x.strip()]
                if len(auth_list) > 2:
                    authors_str = f"{auth_list[0]}; {auth_list[1]} et al."
                else:
                    authors_str = "; ".join(auth_list)
            else:
                authors_str = "—"
            authors_str = shorten(authors_str, 50)
            
            journal = shorten(a.get("Journal/Conference",""), 40)
            
            doi = a.get("DOI","").strip()
            if doi and doi != "-":
                if not doi.startswith("http"):
                    doi_cell = f"[Tautan](https://doi.org/{doi})"
                else:
                    doi_cell = f"[Tautan]({doi})"
            else:
                doi_cell = "—"

            title = title.replace("|", "\\|")
            authors_str = authors_str.replace("|", "\\|")
            journal = journal.replace("|", "\\|")

            lines.append(f"| {i} | {year} | {title} | {authors_str} | {journal} | {doi_cell} |")

        lines.append("")
        lines.append("---")
        lines.append("")

    # Notes
    lines.append("## 4. Catatan Teknis")
    lines.append("")
    lines.append("- Untuk teks abstrak lengkap, rujuk dokumen literature_database.md.")
    lines.append("- Data mentah terstruktur tersedia pada direktori csv/.")
    lines.append("- Kunci API IEEE Xplore dalam antrean persetujuan aktivasi oleh pihak IEEE.")
    lines.append("")
    lines.append(f"*Dokumentasi dibuat secara otomatis pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    content = "\n".join(lines)
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

    print(f"Written {OUTPUT_MD} ({len(content):,} bytes, {len(lines):,} lines)")

if __name__ == "__main__":
    main()
