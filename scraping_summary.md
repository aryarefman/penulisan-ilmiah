# Ringkasan Hasil Scraping & Deduplikasi Jurnal Akademik
**Topik Penelitian**: Arsitektur World Model pada Domain Video: Perbandingan Joint Embedding Predictive Architectures (JEPA) dan Generatif  
**Rentang Pencarian**: 2018 – 2026  
**Format Sesuai**: Sheet `Raw_Articles` pada Excel Protokol SLR  

---

## 1. Statistik Hasil per Basis Data

| No | Basis Data / Sumber | Format / API | Jumlah Mentah | Jumlah Unik Primer |
|---|---|---|---|---|
| 1 | **CrossRef** | `api.crossref.org (Polite Pool)` | 1067 | 1062 |
| 2 | **OpenAlex** | `api.openalex.org` | 919 | 916 |
| 3 | **Scopus** | `api.elsevier.com (API Key)` | 86 | 63 |
| 4 | **ScienceDirect** | `api.elsevier.com (API Key)` | 214 | 187 |
| 5 | **Springer Nature** | `api.springernature.com (API Key)` | 232 | 215 |
| 6 | **Semantic Scholar** | `api.semanticscholar.org` | 198 | 192 |
| 7 | **PubMed** | `eutils.ncbi.nlm.nih.gov` | 23 | 17 |
| 8 | **IEEE Xplore** | `ieeexploreapi.ieee.org (API Key)` | 73 | 45 |
| | **TOTAL KESELURUHAN** | | **2812** | **2697** |

- **Total Entri Mentah Terkumpul**: 2812 artikel
- **Total Duplikat Lintas Basis Data**: 115 artikel
- **Total Artikel Unik (Siap Screening)**: **2697 artikel**

---

## 2. Distribusi Tahun Terbit (Artikel Unik)

| Tahun | Jumlah Artikel | Persentase |
|---|---|---|
| 2027 | 1 | 0.0% |
| 2026 | 787 | 29.2% |
| 2025 | 488 | 18.1% |
| 2024 | 388 | 14.4% |
| 2023 | 286 | 10.6% |
| 2022 | 211 | 7.8% |
| 2021 | 177 | 6.6% |
| 2020 | 137 | 5.1% |
| 2019 | 135 | 5.0% |
| 2018 | 87 | 3.2% |

---

## 3. Tumpang-Tindih Antar Basis Data (Overlap Matrix)

| Pasangan Basis Data | Jumlah Artikel Duplikat yang Ditemukan Bersama |
|---|---|
| IEEE Xplore & Scopus | 18 artikel |
| OpenAlex & Springer Nature | 17 artikel |
| CrossRef & Scopus | 12 artikel |
| OpenAlex & ScienceDirect | 11 artikel |
| CrossRef & ScienceDirect | 10 artikel |
| OpenAlex & Scopus | 9 artikel |
| OpenAlex & Semantic Scholar | 6 artikel |
| CrossRef & OpenAlex | 5 artikel |
| ScienceDirect & Scopus | 5 artikel |
| IEEE Xplore & OpenAlex | 5 artikel |
| OpenAlex & OpenAlex | 3 artikel |
| CrossRef & IEEE Xplore | 3 artikel |
| PubMed & Scopus | 3 artikel |
| IEEE Xplore & Semantic Scholar | 2 artikel |
| OpenAlex & PubMed | 2 artikel |
| Scopus & Semantic Scholar | 1 artikel |
| Scopus & Springer Nature | 1 artikel |
| ScienceDirect & Semantic Scholar | 1 artikel |
| PubMed & PubMed | 1 artikel |

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
   - `csv/all_combined.csv` (2812 baris, mencakup seluruh entri dengan penanda duplikat)
   - `csv/all_unique.csv` (2697 baris, hanya artikel unik untuk tahap screening berikutnya)

Semua kolom CSV sudah 100% presisi mengikuti struktur header pada sheet **Raw_Articles**:
`Article_ID`, `Source_Type`, `Database/Source`, `Search_Date`, `Search_Query`, `Title`, `Authors`, `Year`, `Journal/Conference`, `DOI`, `URL`, `Abstract`, `Document_Type`, `Language`, `Duplicate_Key`, `Duplicate?`, `Notes`.
