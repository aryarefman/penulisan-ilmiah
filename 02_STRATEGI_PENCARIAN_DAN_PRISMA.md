# Strategi Pencarian Komprehensif & Alur PRISMA 2020

> **Dokumen Terkait**: `Search_Strategy` & `PRISMA_Counts` dari protokol SLR  
> **Status**: Tervalidasi & Tereksekusi Sempurna  
> **Tanggal Pembaruan Terakhir**: 22 September 2026

---

## 1. Tujuan & Logika Strategi Pencarian

Strategi pencarian dirancang secara transparan, sistematis, dan dapat direproduksi (*reproducible*) untuk menjaring seluruh studi primer yang mengusulkan, mengevaluasi, memodifikasi, atau membandingkan arsitektur **world model** berbasis representasi laten non-generatif (**JEPA**) dan berbasis generasi piksel (**Generatif / Difusi / Autoregresif**) pada domain video dan simulasi interaktif digital.

### 1.1 Dekonstruksi Konsep Pencarian (Search Concepts)

Pencarian dibangun berdasarkan kombinasi konsep Boolean berjenjang:

$$\text{Search Query} = \mathbf{Konsep}_1 \text{ (World Model)} \;\mathbf{AND}\; \mathbf{Konsep}_2 \text{ (Arsitektur)} \;\mathbf{AND}\; \mathbf{Konsep}_3 \text{ (Tugas Hilir / Video)}$$

```mermaid
flowchart LR
    K1["<b>Konsep 1: Populasi</b><br>'world model'<br>'world models'<br>'world modeling'"]
    K2["<b>Konsep 2: Arsitektur</b><br>'JEPA' OR 'joint embedding'<br>'generative' OR 'diffusion'<br>'Dreamer' OR 'latent dynamics'"]
    K3["<b>Konsep 3: Domain & Tugas</b><br>'video prediction'<br>'representation probing'<br>'planning' OR 'model-based RL'<br>'visual sequence'"]

    K1 --- AND1((AND))
    K2 --- AND1
    AND1 --- AND2((AND))
    K3 --- AND2
    AND2 ==> QUERY[<b>Sintaks Query Terintegrasi</b>]

    style K1 fill:#e1f5fe,stroke:#0288d1
    style K2 fill:#e8f5e9,stroke:#388e3c
    style K3 fill:#fff3e0,stroke:#f57c00
    style QUERY fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
```

---

## 2. Rincian Eksekusi Query per Basis Data Akademik

Pencarian dijalankan secara otomatis melalui antarmuka Application Programming Interface (API) resmi dan polite protocols pada 8 basis data ilmiah terkemuka:

| # | Basis Data Ilmiah | Endpoint / Protokol Akses Riil | Sintaks Query / Parameter Pencarian Aktual | Hasil Mentah | Hasil Unik |
|:---:|:---|:---|:---|:---:|:---:|
| 1 | **CrossRef** | `https://api.crossref.org/works`<br>*(Polite Pool with mailto)* | **14 Kueri Terarah:**<br>• `world model JEPA video prediction`<br>• `joint embedding predictive architecture video`<br>• `world model generative video diffusion`<br>• `V-JEPA video representation self-supervised`<br>• `generative world model reinforcement learning`<br>• `latent dynamics model video prediction`<br>• `video world model visual planning simulation`<br>• `I-JEPA joint embedding predictive architecture`<br>• `autoregressive world model video generation`<br>• `diffusion world model interactive simulation`<br>• `learned dynamics model video reinforcement learning`<br>• `action-conditioned video prediction world model`<br>• `hierarchical JEPA planning robotics`<br>• `spatiotemporal world model video forecasting`<br>*(Filter: Tahun 2018–2026, Type: journal-article)* | **1,067** | **1,062** |
| 2 | **OpenAlex** | `https://api.openalex.org/works`<br>*(Open Catalog REST API)* | **10 Kueri Terstruktur (Q1–Q10):**<br>• `world model JEPA video prediction generative`<br>• `world model video JEPA generative diffusion`<br>• `world model video prediction video generation`<br>• `world model video generation planning`<br>• `V-JEPA I-JEPA representation learning`<br>• `generative world model reinforcement learning`<br>• `latent dynamics model video prediction`<br>• `video world model autoregressive transformer`<br>• `diffusion world model simulation planning`<br>• `world model visual representation self-supervised`<br>*(Filter: from_publication_date:2018-01-01, type:article)* | **919** | **916** |
| 3 | **Springer Nature** | `https://api.springernature.com/meta/v2/json`<br>*(Springer Meta API Key)* | **12 Kueri Spesifik:**<br>• `"world model" video` \| `"world models" video`<br>• `world model JEPA`<br>• `"joint embedding predictive architecture"`<br>• `"generative world model"` \| `"diffusion world model"`<br>• `"video world model"` \| `latent dynamics "video prediction"`<br>• `"visual world model"` \| `"action-conditioned" video world model`<br>• `V-JEPA video` \| `I-JEPA representation learning`<br>*(Filter: Tahun 2018–2026, contentType:Article)* | **232** | **215** |
| 4 | **ScienceDirect** | `https://api.elsevier.com/content/search/sciencedirect`<br>*(Elsevier API Key)* | **4 Kueri Terfokus:**<br>• `("world model" OR "world models") AND ("JEPA" OR "generative" OR "diffusion") AND ("video prediction" OR "planning" OR "probing")`<br>• `("world model" OR "world models") AND ("video prediction" OR "video generation" OR "visual planning")`<br>• `("joint embedding predictive architecture" OR "JEPA" OR "V-JEPA") AND (video OR visual)`<br>• `("generative world model" OR "diffusion world model" OR "video world model")`<br>*(Filter: Tahun 2018–2026)* | **214** | **187** |
| 5 | **Semantic Scholar** | `https://api.semanticscholar.org/graph/v1/paper/search`<br>*(Academic Graph API)* | **10 Kueri Embedding:**<br>• `world model JEPA video prediction generative`<br>• `world model video JEPA generative diffusion`<br>• `world model video prediction video generation`<br>• `JEPA joint embedding predictive architecture video visual`<br>• `generative world model diffusion video`<br>• `V-JEPA video representation learning world model`<br>• `world model reinforcement learning video latent dynamics`<br>• `video world model autoregressive diffusion transformer`<br>• `learned world model visual planning simulation`<br>• `I-JEPA V-JEPA self-supervised video`<br>*(Filter: Tahun 2018–2026, publicationTypes:JournalArticle)* | **198** | **192** |
| 6 | **Scopus** | `https://api.elsevier.com/content/search/scopus`<br>*(Elsevier API Key)* | **6 Kueri Scopus Terpadu:**<br>• `TITLE-ABS-KEY(("world model" OR "world models" OR "learned dynamics model") AND ("JEPA" OR "joint embedding predictive architecture" OR "generative world model" OR "diffusion world model") AND ("video prediction" OR "planning" OR "model-based RL"))`<br>• `TITLE-ABS-KEY(("world model" OR "world models") AND ("video" OR "visual") AND ("JEPA" OR "generative" OR "diffusion" OR "autoregressive"))`<br>• `TITLE-ABS-KEY(("JEPA" OR "joint embedding predictive architecture" OR "V-JEPA" OR "I-JEPA") AND ("video" OR "visual" OR "image" OR "representation"))`<br>• `TITLE-ABS-KEY(("generative world model" OR "diffusion world model" OR "video world model"))`<br>• `TITLE-ABS-KEY(("world model" OR "world models") AND ("video prediction" OR "frame prediction" OR "visual planning"))`<br>• `TITLE-ABS-KEY(("action-conditioned" AND "world model" AND video))`<br>*(Filter: PUBYEAR > 2017, DOCTYPE(ar))* | **86** | **63** |
| 7 | **IEEE Xplore** | `https://ieeexploreapi.ieee.org/api/v1/search/articles`<br>*(IEEE REST API Key)* | **7 Kueri Terarah (Q01–Q07):**<br>• `("world model" OR "world models") AND ("video" OR "video prediction")`<br>• `("world model" OR "world models") AND ("JEPA" OR "joint embedding")`<br>• `("generative world model" OR "diffusion world model") AND ("video")`<br>• `("V-JEPA" OR "I-JEPA") AND ("video" OR "representation")`<br>• `("world model") AND ("reinforcement learning") AND ("video" OR "visual")`<br>• `("latent dynamics") AND ("video" OR "visual planning")`<br>• `("video generation") AND ("world model" OR "simulation")`<br>*(Filter: Tahun 2018–2026, content_type: Journals)* | **73** | **45** |
| 8 | **PubMed** | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`<br>*(esearch.fcgi & efetch.fcgi)* | **5 Kueri Biomedis/Visual:**<br>• `("world model"[Title/Abstract] OR "world models"[Title/Abstract]) AND ("video prediction"[Title/Abstract] OR "visual prediction"[Title/Abstract])`<br>• `("world model"[Title/Abstract]) AND ("reinforcement learning"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract])`<br>• `("JEPA"[Title/Abstract] OR "joint embedding predictive"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract])`<br>• `("generative world model"[Title/Abstract] OR "diffusion world model"[Title/Abstract])`<br>• `("latent dynamics"[Title/Abstract]) AND ("video"[Title/Abstract] OR "visual"[Title/Abstract] OR "planning"[Title/Abstract])`<br>*(Filter: 2018/01/01 s/d 2026/12/31)* | **23** | **17** |
| | **TOTAL KESELURUHAN** | | **Koleksi Gabungan 8 Basis Data Ilmiah Global** | **2,812** | **2,697** |

---

## 3. Diagram Alur PRISMA 2020 (Preferred Reporting Items for Systematic Reviews)

Proses seleksi literatur mengikuti pedoman standar **PRISMA 2020** untuk memastikan transparansi dan keandalan pelaporan:

```mermaid
flowchart TD
    subgraph IDENTIFIKASI ["<b>1. IDENTIFIKASI (Identification)</b>"]
        Raw["<b>Catatan Mentah Teridentifikasi</b><br>(Total: n = 2,812)<br>• CrossRef: 1,067<br>• OpenAlex: 919<br>• Springer Nature: 232<br>• ScienceDirect: 214<br>• Semantic Scholar: 198<br>• Scopus: 86<br>• IEEE Xplore: 73<br>• PubMed: 23"]
        Dedup["<b>Penghapusan Duplikasi (EC1)</b><br>Dihapus n = 115 artikel duplikat<br>berdasarkan normalisasi DOI & Judul"]
        Unique["<b>Total Korpus Unik Siap Screening</b><br>(n = 2,697 artikel)"]
        Raw --> Dedup --> Unique
    end

    subgraph PENYARINGAN ["<b>2. PENYARINGAN (Screening)</b>"]
        Screened["<b>Penyaringan Judul & Abstrak</b><br>(n = 2,697 artikel)"]
        Excluded1["<b>Dieksklusi pada Tahap 1 (n = 2,617)</b><br>• EC2 (Di luar tahun 2018-2026): n = 1<br>• EC3 (Bukan world model / out of scope): n = 1,484<br>• EC4 (Bukan domain video / tanpa dinamika): n = 1,110<br>• EC5 (Abstrak pendek / editorial / non-teknis): n = 2<br>• EC6 (Full text bukan bahasa Inggris): n = 20"]
        Candidates["<b>Pool Lolos ke Tahap 2</b><br>(n = 80 artikel: 65 Candidate + 15 Review)"]
        Unique --> Screened
        Screened --> Excluded1
        Screened --> Candidates
    end

    subgraph KELAYAKAN ["<b>3. KELAYAKAN (Eligibility)</b>"]
        FullText["<b>Pemeriksaan Teks Lengkap (Eligibility)</b><br>(n = 80 artikel)"]
        Excluded2["<b>Dieksklusi pada Tahap 2 (n = 32)</b><br>• EC6 (Full-text paywall tidak dapat diakses): n = 14<br>• EC7 (Artikel non-peer-reviewed/laporan informal): n = 11<br>• EC3/EC4 (Tidak ada evaluasi komparatif/downstream tasks): n = 7"]
        QA_Pool["<b>Kumpulan Penilaian Kualitas (QA)</b><br>(n = 48 artikel)"]
        Candidates --> FullText
        FullText --> Excluded2
        FullText --> QA_Pool
    end

    subgraph INKLUSI ["<b>4. INKLUSI AKHIR (Included)</b>"]
        QA_Eval["<b>Penilaian Kualitas 8 Dimensi (QA1–QA8)</b><br>(Skor Maksimum = 24.0 / 100%)"]
        QA_Excluded["<b>Gagal Ambang Batas QA (&lt;60%)</b><br>(n = 6 artikel dieksklusi)"]
        Included["<b>Artikel Final Masuk Sintesis (Included)</b><br><b>(n = 42 artikel berbobot tinggi)</b><br>• Lolos Kategori Final (&ge;75%): n = 34<br>• Lolos Kategori Review (60-74.9% setelah konsensus): n = 8"]
        QA_Pool --> QA_Eval
        QA_Eval --> QA_Excluded
        QA_Eval --> Included
    end

    style IDENTIFIKASI fill:#f5f5f5,stroke:#616161,stroke-width:2px
    style PENYARINGAN fill:#fff8e1,stroke:#fbc02d,stroke-width:2px
    style KELAYAKAN fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px
    style INKLUSI fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style Included fill:#c8e6c9,stroke:#2e7d32,stroke-width:3px
```

---

## 4. Tabel Rekonsiliasi Metrik PRISMA 2020 (*Working Counts*)

Tabel ini merekonsiliasi seluruh angka operasional yang tersimpan pada sheet `PRISMA_Counts` Excel:

| Metrik PRISMA 2020 | Nilai Numerik | Keterangan & Definisi Operasional |
|:---|:---:|:---|
| **Records identified from databases/registers** | **2,812** | Total catatan mentah yang ditarik dari seluruh 8 API basis data ilmiah resmi. |
| **Records identified from snowballing / other methods** | **0** | Pencarian murni berbasis API terindeks untuk mencegah bias subjektif. |
| **Duplicates removed before screening (EC1)** | **115** | Duplikat lintas basis data yang diidentifikasi melalui kesamaan DOI dan string judul ter-normalisasi. |
| **Records screened (Title & Abstract)** | **2,697** | Jumlah artikel unik primer yang disaring berdasarkan kriteria inklusi/eksklusi awal. |
| **Records excluded during screening (Tahap 1)** | **2,617** | Artikel yang tidak memenuhi IC atau terkena penolakan EC2, EC3, EC4, EC5, EC6. |
| **Reports sought for retrieval (Full-Text)** | **80** | Artikel relevan (65 Candidate + 15 Review) yang diupayakan pengunduhan dokumen teks lengkapnya. |
| **Reports not retrieved** | **14** | Artikel teks lengkap yang tidak dapat diakses institusi (kriteria EC6). |
| **Reports assessed for eligibility** | **66** | Artikel teks lengkap yang dibaca secara komprehensif oleh tim peneliti. |
| **Reports excluded during eligibility** | **18** | Ditolak karena merupakan laporan informal/pre-analisis tanpa detail empiris (EC7) atau tidak mengevaluasi downstream tasks (EC3/EC4). |
| **Candidate studies assessed for Quality (QA)** | **48** | Artikel ilmiah utuh yang dievaluasi dengan matriks QA1 sampai QA8. |
| **Studies excluded after QA (<60% score)** | **6** | Studi yang memiliki metodologi lemah atau dokumentasi evaluasi yang tidak memadai. |
| **Final studies included in qualitative synthesis** | **42** | **Koleksi studi primer final yang dianalisis secara mendalam untuk menjawab RQ-01 s/d RQ-06.** |

---

## 5. Protokol Audit & Reproduksibilitas Data

Seluruh proses penarikan data dan penyaringan dicatat dalam skrip otomatis yang tersimpan pada repositori ini:
- `csv/all_combined.csv`: Data mentah gabungan (2.812 baris).
- `csv/all_unique.csv`: Data unik primer hasil deduplikasi (2.697 baris).
- `csv/screening.csv`: Keputusan screening lengkap untuk 2.812 baris.
- `clean_and_repair_datasets.py`: Skrip normalisasi encoding UTF-8, pembersihan karakter anomali, dan deteksi duplikat.
- `literature_summary.md`: Tabel ringkas satu baris per artikel untuk navigasi cepat.
- `literature_database.md`: Katalog lengkap seluruh 2.697 artikel unik beserta abstrak utuhnya.
