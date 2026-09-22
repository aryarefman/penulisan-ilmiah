#!/usr/bin/env python3
"""
Generate a clean, well-structured Markdown report from all_unique.csv.
Groups articles by database source, sorted by year (desc) then title.
"""

import csv
import sys
import re
import textwrap
from collections import defaultdict
from datetime import datetime

CSV_FILE = r"csv/all_unique.csv"
OUTPUT_MD = r"literature_database.md"

def clean_text(text):
    """Clean text: strip HTML, normalize whitespace."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)  # strip HTML
    text = re.sub(r'&[a-z]+;', ' ', text)  # strip HTML entities
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def truncate_abstract(abstract, max_chars=500):
    """Truncate abstract to max_chars, ending at a sentence boundary if possible."""
    if not abstract or len(abstract) <= max_chars:
        return abstract
    # Try to cut at sentence boundary
    truncated = abstract[:max_chars]
    last_period = truncated.rfind('.')
    if last_period > max_chars * 0.6:
        return truncated[:last_period + 1] + " *(…)*"
    return truncated.rstrip() + "… *(truncated)*"

def format_doi_link(doi):
    """Format DOI as clickable link."""
    if not doi or doi.strip() == '-' or doi.strip() == '':
        return "—"
    doi = doi.strip()
    if doi.startswith("http"):
        return f"[{doi}]({doi})"
    return f"[{doi}](https://doi.org/{doi})"

def main():
    # Read CSV
    articles = []
    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            articles.append(row)
    
    print(f"Read {len(articles)} articles from CSV")
    
    # Group by database
    by_db = defaultdict(list)
    for art in articles:
        db = art.get("Database/Source", "Unknown").strip()
        by_db[db].append(art)
    
    # Sort each group by year (desc), then title
    for db in by_db:
        by_db[db].sort(key=lambda a: (
            -int(float(a.get("Year", "0") or "0")),
            a.get("Title", "").lower()
        ))
    
    # Database display order
    db_order = [
        "CrossRef",
        "OpenAlex", 
        "Springer Nature",
        "ScienceDirect",
        "Semantic Scholar",
        "Scopus",
        "PubMed",
        "IEEE Xplore",
    ]
    # Add any databases not in the order list
    for db in sorted(by_db.keys()):
        if db not in db_order:
            db_order.append(db)
    
    # Database descriptions
    db_desc = {
        "CrossRef": "Open metadata API (Polite Pool) — DOI registration agency covering most scholarly publishers.",
        "OpenAlex": "Open catalog of scholarly works, authors, venues, institutions, and concepts.",
        "Springer Nature": "Publisher API (API Key) — Springer, Nature, Palgrave Macmillan, BMC journals.",
        "ScienceDirect": "Elsevier API (API Key) — Full-text scientific database by Elsevier.",
        "Semantic Scholar": "AI-powered research tool by Allen Institute for AI.",
        "Scopus": "Elsevier API (API Key) — Largest abstract and citation database of peer-reviewed literature.",
        "PubMed": "NCBI E-Utilities — Biomedical and life sciences literature from NLM/NIH.",
        "IEEE Xplore": "IEEE Digital Library — Electrical engineering, computer science, and electronics.",
    }
    
    # Statistics
    total = len(articles)
    with_abstract = sum(1 for a in articles if clean_text(a.get("Abstract", "")))
    with_doi = sum(1 for a in articles if a.get("DOI", "").strip() and a.get("DOI", "").strip() != '-')
    
    # Year distribution
    year_dist = defaultdict(int)
    for a in articles:
        y = a.get("Year", "")
        if y:
            try:
                year_dist[int(float(y))] += 1
            except:
                year_dist["Unknown"] += 1
    
    # ─── Generate Markdown ───
    lines = []
    
    # Header
    lines.append("# Basis Data Literatur — Systematic Literature Review")
    lines.append("")
    lines.append("**Topik:** Arsitektur World Model pada Domain Video: Perbandingan Joint Embedding")
    lines.append("Predictive Architectures (JEPA) dan Generatif")
    lines.append("")
    lines.append(f"**Tanggal Pembuatan:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Rentang Tahun:** 2018 – 2026")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Summary table
    lines.append("## 1. Ringkasan Statistik")
    lines.append("")
    lines.append("### 1.1 Distribusi per Basis Data")
    lines.append("")
    lines.append("| No | Basis Data | Jumlah Artikel | % Total |")
    lines.append("|:--:|:---|:--:|:--:|")
    for i, db in enumerate(db_order, 1):
        if db in by_db:
            count = len(by_db[db])
            pct = count / total * 100
            lines.append(f"| {i} | **{db}** | {count:,} | {pct:.1f}% |")
    lines.append(f"| | **TOTAL** | **{total:,}** | **100%** |")
    lines.append("")
    
    # Data completeness
    lines.append("### 1.2 Kelengkapan Data")
    lines.append("")
    lines.append("| Kolom | Terisi | Persentase |")
    lines.append("|:---|:--:|:--:|")
    lines.append(f"| Judul | {total:,} | 100% |")
    lines.append(f"| DOI | {with_doi:,} | {with_doi/total*100:.1f}% |")
    lines.append(f"| Abstrak | {with_abstract:,} | {with_abstract/total*100:.1f}% |")
    lines.append("")
    
    # Year distribution
    lines.append("### 1.3 Distribusi Tahun Terbit")
    lines.append("")
    lines.append("| Tahun | Jumlah Artikel |")
    lines.append("|:--:|:--:|")
    for year in sorted(k for k in year_dist.keys() if isinstance(k, int)):
        count = year_dist[year]
        lines.append(f"| {year} | {count:,} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Articles per database
    lines.append("## 2. Koleksi Artikel Ilmiah per Basis Data")
    lines.append("")
    for db in db_order:
        if db not in by_db:
            continue
        
        db_articles = by_db[db]
        desc = db_desc.get(db, "")
        
        lines.append(f"### Basis Data: {db}")
        lines.append("")
        if desc:
            lines.append(f"> {desc}")
            lines.append("")
        lines.append(f"**Total:** {len(db_articles):,} artikel")
        lines.append("")
        
        # Group by year within each database
        by_year = defaultdict(list)
        for art in db_articles:
            y = art.get("Year", "")
            try:
                by_year[int(float(y))].append(art)
            except:
                by_year[0].append(art)
        
        for year in sorted(by_year.keys(), reverse=True):
            year_arts = by_year[year]
            year_label = str(year) if year > 0 else "Tahun Tidak Diketahui"
            lines.append(f"#### Tahun {year_label} ({len(year_arts)} artikel)")
            lines.append("")
            
            for idx, art in enumerate(year_arts, 1):
                title = clean_text(art.get("Title", "Untitled"))
                authors = clean_text(art.get("Authors", ""))
                journal = clean_text(art.get("Journal/Conference", ""))
                doi = art.get("DOI", "").strip()
                url = art.get("URL", "").strip()
                abstract = clean_text(art.get("Abstract", ""))
                doc_type = art.get("Document_Type", "").strip()
                lang = art.get("Language", "").strip()
                article_id = art.get("Article_ID", "").strip()
                
                # Title with link
                if url:
                    lines.append(f"**{idx}. [{title}]({url})**")
                elif doi and not doi.startswith("http"):
                    lines.append(f"**{idx}. [{title}](https://doi.org/{doi})**")
                else:
                    lines.append(f"**{idx}. {title}**")
                lines.append("")
                
                # Metadata line
                meta_parts = []
                if authors:
                    author_list = authors.split(";")
                    if len(author_list) > 3:
                        short_authors = "; ".join(a.strip() for a in author_list[:3]) + f" *et al.* ({len(author_list)} authors)"
                    else:
                        short_authors = authors
                    meta_parts.append(f"Penulis: {short_authors}")
                if journal:
                    meta_parts.append(f"Jurnal: *{journal}*")
                if doc_type:
                    meta_parts.append(f"Tipe: {doc_type}")
                if lang:
                    meta_parts.append(f"Bahasa: {lang}")
                
                if meta_parts:
                    lines.append(" | ".join(meta_parts))
                    lines.append("")
                
                # DOI
                if doi and doi != '-':
                    if doi.startswith("http"):
                        lines.append(f"DOI: [{doi}]({doi})")
                    else:
                        lines.append(f"DOI: [`{doi}`](https://doi.org/{doi})")
                    lines.append("")
                
                # Abstract (truncated)
                if abstract:
                    short_abstract = truncate_abstract(abstract, 400)
                    lines.append(f"<details><summary>Abstrak</summary>")
                    lines.append("")
                    lines.append(f"{short_abstract}")
                    lines.append("")
                    lines.append("</details>")
                    lines.append("")
                
                lines.append("---")
                lines.append("")
        
        lines.append("")
    
    # Footer
    lines.append("## 3. Catatan Teknis")
    lines.append("")
    lines.append("- Data dikumpulkan melalui API resmi dari masing-masing basis data akademik.")
    lines.append("- Deduplikasi dilakukan berdasarkan DOI dan normalisasi judul.")
    lines.append("- Teks abstrak yang terlalu panjang dipotong untuk keterbacaan; lihat tautan DOI untuk versi lengkap.")
    lines.append("- Kunci API IEEE Xplore dalam proses antrean persetujuan aktivasi oleh pihak IEEE.")
    lines.append("")
    lines.append(f"*Dokumentasi dibuat pada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Write
    md_content = "\n".join(lines)
    with open(OUTPUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md_content)
    
    file_size = len(md_content.encode("utf-8"))
    print(f"Written to {OUTPUT_MD} ({file_size:,} bytes, {len(lines):,} lines)")
    print(f"Articles: {total:,} across {len(by_db)} databases")

if __name__ == "__main__":
    main()
