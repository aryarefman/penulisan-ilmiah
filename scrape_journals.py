"""
Scraping Jurnal Akademik — World Model JEPA vs Generatif
Sumber: Semantic Scholar, OpenAlex, CrossRef, PubMed
Output: raw_json/<source>.json + csv/<source>.csv
"""

import json
import csv
import os
import time
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(BASE_DIR, "raw_json")
CSV_DIR = os.path.join(BASE_DIR, "csv")
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

SEARCH_DATE = datetime.now().strftime("%Y-%m-%d")

# CSV columns matching Raw_Articles sheet
CSV_HEADERS = [
    "Article_ID", "Source_Type", "Database/Source", "Search_Date",
    "Search_Query", "Title", "Authors", "Year", "Journal/Conference",
    "DOI", "URL", "Abstract", "Document_Type", "Language",
    "Duplicate_Key", "Duplicate?", "Notes"
]

# Multiple query sets from specific to general
QUERY_SETS = {
    "Q1_specific": '("world model" OR "world models") AND ("JEPA" OR "joint embedding predictive architecture" OR "V-JEPA" OR "I-JEPA" OR "generative world model" OR "diffusion world model") AND ("video prediction" OR "planning" OR "model-based reinforcement learning")',
    "Q2_medium": '("world model" OR "world models") AND ("video" OR "visual") AND ("JEPA" OR "generative" OR "diffusion" OR "autoregressive")',
    "Q3_general_wm": '("world model") AND ("video prediction" OR "video generation" OR "visual planning")',
    "Q4_jepa_focus": '("JEPA" OR "joint embedding predictive architecture") AND ("video" OR "visual" OR "representation learning")',
    "Q5_gen_wm": '("generative world model" OR "diffusion world model" OR "video world model")',
}


def http_get(url, headers=None, retries=3, delay=2):
    """Simple HTTP GET with retries."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "AcademicSLR/1.0 (research scraper; mailto:research@example.com)")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limited
                wait = delay * (2 ** attempt)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            elif e.code == 504 or e.code == 503:
                wait = delay * (2 ** attempt)
                print(f"  Server error {e.code}, retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"  HTTP Error {e.code}: {e.reason}")
                return None
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def http_get_text(url, retries=3, delay=2):
    """HTTP GET returning raw text (for XML)."""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "AcademicSLR/1.0")
    
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return None


def make_duplicate_key(title, year):
    """Create a simple duplicate key from title + year."""
    if not title:
        return ""
    clean = title.lower().strip()
    # Remove common punctuation
    for ch in ".:;,!?'\"()[]{}":
        clean = clean.replace(ch, "")
    words = clean.split()[:8]
    return f"{'_'.join(words)}_{year}" if year else '_'.join(words)


def save_json(data, source_name):
    path = os.path.join(JSON_DIR, f"{source_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved JSON: {path} ({len(data) if isinstance(data, list) else 'dict'} items)")


def save_csv(rows, source_name):
    path = os.path.join(CSV_DIR, f"{source_name}.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    print(f"  Saved CSV: {path} ({len(rows)} rows)")


# ============================================================
# 1. SEMANTIC SCHOLAR
# ============================================================
def search_semantic_scholar():
    print("\n" + "="*60)
    print("SEMANTIC SCHOLAR")
    print("="*60)
    
    all_papers = []
    seen_ids = set()
    
    # Semantic Scholar uses simpler query syntax
    ss_queries = {
        "Q1": "world model JEPA video prediction generative",
        "Q2": "world model video JEPA generative diffusion",
        "Q3": "world model video prediction video generation",
        "Q4": "JEPA joint embedding predictive architecture video visual",
        "Q5": "generative world model diffusion video",
        "Q6": "V-JEPA video representation learning world model",
        "Q7": "world model reinforcement learning video latent dynamics",
        "Q8": "video world model autoregressive diffusion transformer",
        "Q9": "learned world model visual planning simulation",
        "Q10": "I-JEPA V-JEPA self-supervised video",
    }
    
    for qname, query in ss_queries.items():
        print(f"\n  Query {qname}: {query}")
        offset = 0
        limit = 100
        query_total = 0
        
        while offset < 500:  # Max 500 per query
            params = urllib.parse.urlencode({
                "query": query,
                "offset": offset,
                "limit": limit,
                "year": "2018-2026",
                "fields": "title,authors,year,abstract,venue,externalIds,url,publicationTypes,citationCount,openAccessPdf",
                "publicationTypes": "JournalArticle"
            })
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
            
            data = http_get(url)
            if not data or "data" not in data:
                break
            
            papers = data["data"]
            if not papers:
                break
            
            for p in papers:
                pid = p.get("paperId", "")
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    all_papers.append(p)
                    query_total += 1
            
            total_available = data.get("total", 0)
            offset += limit
            if offset >= total_available:
                break
            
            time.sleep(1.5)  # Rate limit: ~1 req/sec for unauthenticated
        
        print(f"    -> {query_total} new papers (total unique: {len(all_papers)})")
        time.sleep(1)
    
    # Save raw JSON
    save_json(all_papers, "semantic_scholar")
    
    # Convert to CSV rows
    csv_rows = []
    for i, p in enumerate(all_papers, 1):
        ext_ids = p.get("externalIds") or {}
        doi = ext_ids.get("DOI", "")
        authors = "; ".join([a.get("name", "") for a in (p.get("authors") or [])])
        title = p.get("title", "")
        year = str(p.get("year", ""))
        venue = p.get("venue", "")
        pub_types = ", ".join(p.get("publicationTypes") or [])
        
        csv_rows.append({
            "Article_ID": f"SS-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "Semantic Scholar",
            "Search_Date": SEARCH_DATE,
            "Search_Query": "Multiple queries (Q1-Q10)",
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": p.get("url", ""),
            "Abstract": (p.get("abstract") or "")[:5000],
            "Document_Type": pub_types if pub_types else "Journal Article",
            "Language": "English",
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Citations: {p.get('citationCount', 'N/A')}"
        })
    
    save_csv(csv_rows, "semantic_scholar")
    return len(csv_rows)


# ============================================================
# 2. OPENALEX
# ============================================================
def search_openalex():
    print("\n" + "="*60)
    print("OPENALEX")
    print("="*60)
    
    all_works = []
    seen_ids = set()
    
    # OpenAlex search queries
    oa_queries = {
        "Q1": "world model JEPA video prediction",
        "Q2": "world model generative video diffusion",
        "Q3": "joint embedding predictive architecture video",
        "Q4": "world model video generation planning",
        "Q5": "V-JEPA I-JEPA representation learning",
        "Q6": "generative world model reinforcement learning",
        "Q7": "latent dynamics model video prediction",
        "Q8": "video world model autoregressive transformer",
        "Q9": "diffusion world model simulation planning",
        "Q10": "world model visual representation self-supervised",
    }
    
    for qname, query in oa_queries.items():
        print(f"\n  Query {qname}: {query}")
        page = 1
        query_total = 0
        
        while page <= 5:  # Max 5 pages per query (25 per page = 125)
            params = urllib.parse.urlencode({
                "search": query,
                "filter": "from_publication_date:2018-01-01,to_publication_date:2026-12-31,type:article",
                "per_page": 50,
                "page": page,
                "select": "id,doi,title,authorships,publication_year,primary_location,abstract_inverted_index,type,language,cited_by_count",
                "mailto": "research@example.com"
            })
            url = f"https://api.openalex.org/works?{params}"
            
            data = http_get(url)
            if not data or "results" not in data:
                break
            
            results = data["results"]
            if not results:
                break
            
            for w in results:
                wid = w.get("id", "")
                if wid not in seen_ids:
                    seen_ids.add(wid)
                    all_works.append(w)
                    query_total += 1
            
            meta = data.get("meta", {})
            total_count = meta.get("count", 0)
            if page * 50 >= total_count:
                break
            
            page += 1
            time.sleep(0.5)
        
        print(f"    -> {query_total} new works (total unique: {len(all_works)})")
        time.sleep(0.5)
    
    save_json(all_works, "openalex")
    
    # Convert to CSV
    csv_rows = []
    for i, w in enumerate(all_works, 1):
        # Reconstruct abstract from inverted index
        abstract = ""
        abs_inv = w.get("abstract_inverted_index")
        if abs_inv:
            word_positions = []
            for word, positions in abs_inv.items():
                for pos in positions:
                    word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join([wp[1] for wp in word_positions])
        
        # Authors
        authors = "; ".join([
            a.get("author", {}).get("display_name", "")
            for a in (w.get("authorships") or [])
        ])
        
        # Venue/Journal
        primary_loc = w.get("primary_location") or {}
        source = primary_loc.get("source") or {}
        venue = source.get("display_name", "")
        
        doi_raw = w.get("doi", "") or ""
        doi = doi_raw.replace("https://doi.org/", "") if doi_raw else ""
        
        title = w.get("title", "") or ""
        year = str(w.get("publication_year", ""))
        
        csv_rows.append({
            "Article_ID": f"OA-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "OpenAlex",
            "Search_Date": SEARCH_DATE,
            "Search_Query": "Multiple queries (Q1-Q10)",
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": doi_raw if doi_raw else w.get("id", ""),
            "Abstract": abstract[:5000],
            "Document_Type": w.get("type", "article"),
            "Language": w.get("language", "en"),
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Citations: {w.get('cited_by_count', 'N/A')}"
        })
    
    save_csv(csv_rows, "openalex")
    return len(csv_rows)


# ============================================================
# 3. CROSSREF
# ============================================================
def search_crossref():
    print("\n" + "="*60)
    print("CROSSREF")
    print("="*60)
    
    all_items = []
    seen_dois = set()
    
    cr_queries = {
        "Q1": "world model JEPA video prediction generative",
        "Q2": "joint embedding predictive architecture video visual",
        "Q3": "generative world model video diffusion autoregressive",
        "Q4": "world model video generation planning reinforcement learning",
        "Q5": "V-JEPA I-JEPA self-supervised video representation",
        "Q6": "latent dynamics model video prediction world",
        "Q7": "world model visual simulation planning",
        "Q8": "video world model transformer diffusion",
    }
    
    for qname, query in cr_queries.items():
        print(f"\n  Query {qname}: {query}")
        offset = 0
        query_total = 0
        
        while offset < 200:
            params = urllib.parse.urlencode({
                "query": query,
                "filter": "from-pub-date:2018-01-01,until-pub-date:2026-12-31,type:journal-article",
                "rows": 50,
                "offset": offset,
                "select": "DOI,title,author,published-print,published-online,container-title,abstract,type,language,is-referenced-by-count,URL,subject",
                "mailto": "research@example.com"
            })
            url = f"https://api.crossref.org/works?{params}"
            
            data = http_get(url)
            if not data or "message" not in data:
                break
            
            items = data["message"].get("items", [])
            if not items:
                break
            
            for item in items:
                doi = item.get("DOI", "")
                if doi and doi not in seen_dois:
                    seen_dois.add(doi)
                    all_items.append(item)
                    query_total += 1
            
            total_results = data["message"].get("total-results", 0)
            offset += 50
            if offset >= total_results or offset >= 200:
                break
            
            time.sleep(1)
        
        print(f"    -> {query_total} new items (total unique: {len(all_items)})")
        time.sleep(0.5)
    
    save_json(all_items, "crossref")
    
    # Convert to CSV
    csv_rows = []
    for i, item in enumerate(all_items, 1):
        # Authors
        authors_list = item.get("author", [])
        authors = "; ".join([
            f"{a.get('family', '')}, {a.get('given', '')}" if a.get('family') else a.get('name', '')
            for a in authors_list
        ])
        
        # Year
        pub_date = item.get("published-print") or item.get("published-online") or {}
        date_parts = pub_date.get("date-parts", [[None]])[0]
        year = str(date_parts[0]) if date_parts and date_parts[0] else ""
        
        # Title
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        
        # Journal
        container = item.get("container-title", [])
        venue = container[0] if container else ""
        
        # Abstract (may contain HTML tags)
        abstract = item.get("abstract", "")
        # Basic HTML tag removal
        import re
        abstract = re.sub(r'<[^>]+>', '', abstract) if abstract else ""
        
        doi = item.get("DOI", "")
        
        csv_rows.append({
            "Article_ID": f"CR-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "CrossRef",
            "Search_Date": SEARCH_DATE,
            "Search_Query": "Multiple queries (Q1-Q8)",
            "Title": title,
            "Authors": authors,
            "Year": year,
            "Journal/Conference": venue,
            "DOI": doi,
            "URL": item.get("URL", f"https://doi.org/{doi}"),
            "Abstract": abstract[:5000],
            "Document_Type": item.get("type", "journal-article"),
            "Language": item.get("language", "en"),
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"Citations: {item.get('is-referenced-by-count', 'N/A')}"
        })
    
    save_csv(csv_rows, "crossref")
    return len(csv_rows)


# ============================================================
# 4. PUBMED (NCBI E-Utilities)
# ============================================================
def search_pubmed():
    print("\n" + "="*60)
    print("PUBMED (NCBI E-Utilities)")
    print("="*60)
    
    all_articles = []
    seen_pmids = set()
    
    # PubMed queries - more biomedical/general terms
    pm_queries = {
        "Q1": '("world model"[Title/Abstract] OR "world models"[Title/Abstract]) AND ("video prediction"[Title/Abstract] OR "visual prediction"[Title/Abstract])',
        "Q2": '("world model"[Title/Abstract]) AND ("reinforcement learning"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract])',
        "Q3": '("JEPA"[Title/Abstract] OR "joint embedding predictive"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract])',
        "Q4": '("generative world model"[Title/Abstract] OR "diffusion world model"[Title/Abstract])',
        "Q5": '("latent dynamics"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract] OR "planning"[Title/Abstract])',
    }
    
    for qname, query in pm_queries.items():
        print(f"\n  Query {qname}: {query[:80]}...")
        
        # Step 1: ESearch to get PMIDs
        search_params = urllib.parse.urlencode({
            "db": "pubmed",
            "term": query,
            "retmax": 200,
            "retmode": "json",
            "mindate": "2018/01/01",
            "maxdate": "2026/12/31",
            "datetype": "pdat",
            "usehistory": "n"
        })
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{search_params}"
        
        search_data = http_get(search_url)
        if not search_data or "esearchresult" not in search_data:
            continue
        
        id_list = search_data["esearchresult"].get("idlist", [])
        new_ids = [pid for pid in id_list if pid not in seen_pmids]
        
        if not new_ids:
            print(f"    -> 0 new articles")
            continue
        
        seen_pmids.update(new_ids)
        
        # Step 2: EFetch to get full records
        # Process in batches of 50
        for batch_start in range(0, len(new_ids), 50):
            batch = new_ids[batch_start:batch_start + 50]
            fetch_params = urllib.parse.urlencode({
                "db": "pubmed",
                "id": ",".join(batch),
                "retmode": "xml",
                "rettype": "abstract"
            })
            fetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{fetch_params}"
            
            xml_text = http_get_text(fetch_url)
            if not xml_text:
                continue
            
            try:
                root = ET.fromstring(xml_text)
                for article_elem in root.findall(".//PubmedArticle"):
                    article_data = parse_pubmed_article(article_elem)
                    if article_data:
                        all_articles.append(article_data)
            except ET.ParseError as e:
                print(f"    XML parse error: {e}")
            
            time.sleep(0.5)
        
        print(f"    -> {len(new_ids)} new articles (total: {len(all_articles)})")
        time.sleep(1)
    
    save_json(all_articles, "pubmed")
    
    # Convert to CSV
    csv_rows = []
    for i, a in enumerate(all_articles, 1):
        title = a.get("title", "")
        year = a.get("year", "")
        
        csv_rows.append({
            "Article_ID": f"PM-{i:04d}",
            "Source_Type": "API",
            "Database/Source": "PubMed",
            "Search_Date": SEARCH_DATE,
            "Search_Query": "Multiple queries (Q1-Q5)",
            "Title": title,
            "Authors": a.get("authors", ""),
            "Year": year,
            "Journal/Conference": a.get("journal", ""),
            "DOI": a.get("doi", ""),
            "URL": f"https://pubmed.ncbi.nlm.nih.gov/{a.get('pmid', '')}/",
            "Abstract": a.get("abstract", "")[:5000],
            "Document_Type": a.get("pub_type", "Journal Article"),
            "Language": a.get("language", "English"),
            "Duplicate_Key": make_duplicate_key(title, year),
            "Duplicate?": "",
            "Notes": f"PMID: {a.get('pmid', '')}"
        })
    
    save_csv(csv_rows, "pubmed")
    return len(csv_rows)


def parse_pubmed_article(article_elem):
    """Parse a PubmedArticle XML element into a dict."""
    try:
        medline = article_elem.find(".//MedlineCitation")
        if medline is None:
            return None
        
        pmid_elem = medline.find("PMID")
        pmid = pmid_elem.text if pmid_elem is not None else ""
        
        article = medline.find("Article")
        if article is None:
            return None
        
        # Title
        title_elem = article.find("ArticleTitle")
        title = title_elem.text if title_elem is not None else ""
        
        # Abstract
        abstract_parts = []
        abstract_elem = article.find("Abstract")
        if abstract_elem is not None:
            for at in abstract_elem.findall("AbstractText"):
                label = at.get("Label", "")
                text = "".join(at.itertext())
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
        abstract = " ".join(abstract_parts)
        
        # Authors
        authors = []
        author_list = article.find("AuthorList")
        if author_list is not None:
            for auth in author_list.findall("Author"):
                last = auth.find("LastName")
                first = auth.find("ForeName")
                if last is not None:
                    name = last.text
                    if first is not None:
                        name = f"{last.text}, {first.text}"
                    authors.append(name)
        
        # Journal
        journal_elem = article.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else ""
        
        # Year
        pub_date = article.find(".//Journal/JournalIssue/PubDate")
        year = ""
        if pub_date is not None:
            year_elem = pub_date.find("Year")
            if year_elem is not None:
                year = year_elem.text
            else:
                medline_date = pub_date.find("MedlineDate")
                if medline_date is not None and medline_date.text:
                    year = medline_date.text[:4]
        
        # DOI
        doi = ""
        for eid in article.findall(".//ELocationID"):
            if eid.get("EIdType") == "doi":
                doi = eid.text
                break
        if not doi:
            pubmed_data = article_elem.find("PubmedData")
            if pubmed_data is not None:
                for aid in pubmed_data.findall(".//ArticleId"):
                    if aid.get("IdType") == "doi":
                        doi = aid.text
                        break
        
        # Language
        lang_elem = article.find("Language")
        language = lang_elem.text if lang_elem is not None else "eng"
        
        # Publication types
        pub_types = []
        for pt in article.findall(".//PublicationType"):
            pub_types.append(pt.text)
        
        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": "; ".join(authors),
            "journal": journal,
            "year": year,
            "doi": doi,
            "language": language,
            "pub_type": ", ".join(pub_types) if pub_types else "Journal Article"
        }
    except Exception as e:
        print(f"    Parse error: {e}")
        return None


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("SCRAPING JURNAL AKADEMIK")
    print("Topik: World Model - JEPA vs Generatif (Video Domain)")
    print(f"Tanggal: {SEARCH_DATE}")
    print("=" * 60)
    
    results = {}
    
    # 1. Semantic Scholar
    try:
        results["Semantic Scholar"] = search_semantic_scholar()
    except Exception as e:
        print(f"ERROR Semantic Scholar: {e}")
        results["Semantic Scholar"] = 0
    
    # 2. OpenAlex
    try:
        results["OpenAlex"] = search_openalex()
    except Exception as e:
        print(f"ERROR OpenAlex: {e}")
        results["OpenAlex"] = 0
    
    # 3. CrossRef
    try:
        results["CrossRef"] = search_crossref()
    except Exception as e:
        print(f"ERROR CrossRef: {e}")
        results["CrossRef"] = 0
    
    # 4. PubMed
    try:
        results["PubMed"] = search_pubmed()
    except Exception as e:
        print(f"ERROR PubMed: {e}")
        results["PubMed"] = 0
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total = 0
    for source, count in results.items():
        print(f"  {source:25s}: {count:5d} articles")
        total += count
    print(f"  {'TOTAL':25s}: {total:5d} articles")
    print(f"\nOutput directories:")
    print(f"  JSON: {JSON_DIR}")
    print(f"  CSV:  {CSV_DIR}")
    print("\nDone!")
